from fpdf import FPDF
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm


class AIProspectResearcher:
    def __init__(self):
        # Initialize summarizer model
        self.setup_ai_model()

    def setup_ai_model(self):
        """Set up the AI summarization model."""
        try:
            # Using a summarization model from Hugging Face
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except ModuleNotFoundError as e:
            print("Error: 'transformers' module not found. Please install it using 'pip install transformers'.", str(e))
            self.summarizer = None

    def scrape_website(self, url: str):
        """Scrape the website to get the title, description, and relevant text."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Collecting title and meta description
            title = soup.find('title').get_text() if soup.find('title') else "No title found"
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc else "No meta description found"
            
            # Collecting additional main content (h1, h2, p tags)
            content = ''
            for tag in soup.find_all(['h1', 'h2', 'p']):
                content += tag.get_text(separator=" ", strip=True) + ' '

            return {
                "title": title,
                "description": description,
                "content": content
            }
        except Exception as e:
            print(f"Error while scraping {url}: {str(e)}")
            return None

    def summarize_content(self, content: str, max_chunk_length=500):
        """Summarize content in chunks, dynamically adjusting max_length with progress feedback."""
        if not self.summarizer:
            return "Summarizer model is not available."
        
        chunks = [content[i:i + max_chunk_length] for i in range(0, len(content), max_chunk_length)]
        summarized_text = ''
        
        print("Summarizing content... Please wait.")
        for chunk in tqdm(chunks, desc="Progress", unit="chunk"):
            input_length = len(chunk.split())
            max_len = min(120, int(input_length * 0.6))  # Max length: 60% of input, capped at 120
            min_len = min(30, int(input_length * 0.3))   # Min length: 30% of input, capped at 30

            summary = self.summarizer(chunk, max_length=max_len, min_length=min_len, do_sample=False)
            summarized_text += summary[0]['summary_text'] + ' '

        return summarized_text.strip()

    def create_pdf(self, data, filename="Prospect_Report.pdf"):
        """Create a styled PDF with summarized content."""
        pdf = FPDF()
        pdf.add_page()

        # Title section
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Prospect Report: {data['title']}", ln=True, align='C')

        # Description section
        pdf.set_font("Arial", "I", 12)
        pdf.cell(0, 10, "Website Description:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, data['description'], align='L')

        # Summarized Content section
        pdf.set_font("Arial", "I", 12)
        pdf.cell(0, 10, "Summarized Content:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, data['summarized_content'], align='L')

        # Footer with page number
        pdf.set_y(-15)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, f"Page {pdf.page_no()}", 0, 0, 'C')

        pdf.output(filename)
        return filename

    def generate_report(self, url: str, create_pdf=None, output_filename="Prospect_Report.pdf"):
        """Main function to generate the prospect research report."""
        # Step 1: Scrape the website
        scraped_data = self.scrape_website(url)
        if not scraped_data:
            print("Failed to retrieve content from the website.")
            return None
        
        # Step 2: Summarize the content
        scraped_data['summarized_content'] = self.summarize_content(scraped_data['content'])
        print("Summarized content:", scraped_data['summarized_content'])
        
        # Step 3: Generate PDF report
        if create_pdf == "YES":
            pdf_file = self.create_pdf(scraped_data, filename=output_filename)
            return pdf_file

# Example usage
researcher = AIProspectResearcher()
report = researcher.generate_report(input("Enter a website URL: (EXAMPLE==>https://viso.ai/) "), input("If you want to save the report, write YES or press ENTER for pass: "))

