import requests
from bs4 import BeautifulSoup
import re
from transformers import pipeline
import os
from fpdf import FPDF

class AIProspectResearcher:
    def __init__(self):
        self.setup_ai_model()

    def setup_ai_model(self):
        # Set up an AI model for summarization using Hugging Face's transformers library
        try:
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except ModuleNotFoundError as e:
            print("Error: 'transformers' module not found. Please install it using 'pip install transformers'.", str(e))
            self.summarizer = None

    def scrape_website(self, url: str):
        """Scrape website content including title, description, and additional info like contact details."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract general content
            content = {
                'title': soup.title.string if soup.title else '',
                'description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else '',
                'text': ' '.join([p.get_text() for p in soup.find_all('p')])
            }
            
            # Extract additional information (year founded, goals, etc.)
            additional_info = {
                'year_founded': self.extract_year_founded(soup),
                'goals': self.extract_goals(soup),
                'objectives': self.extract_objectives(soup),
                'innovations': self.extract_innovations(soup),
                'contact_info': self.extract_contact_info(soup)
            }
            print(content)
            
            return content, additional_info
        
        except requests.exceptions.RequestException as e:
            print(f"Error scraping website: {str(e)}")
            return {}, {}

    def extract_year_founded(self, soup):
        """Extract the year the company was founded."""
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().lower()
            if 'founded' in text:
                match = re.search(r'(\d{4})', text)
                if match:
                    return match.group(0)
        return "Not available"

    def extract_goals(self, soup):
        """Extract company goals from the webpage."""
        return self.extract_keyword_sentences(soup, ['goal', 'mission'])

    def extract_objectives(self, soup):
        """Extract company objectives from the webpage."""
        return self.extract_keyword_sentences(soup, ['objective', 'vision'])

    def extract_innovations(self, soup):
        """Extract company innovations from the webpage."""
        return self.extract_keyword_sentences(soup, ['innovation', 'new technology'])

    def extract_contact_info(self, soup):
        """Extract contact information (email) from the webpage."""
        contact_info = []
        email_links = soup.find_all('a', href=re.compile(r'mailto'))
        for link in email_links:
            contact_info.append(link.get('href').replace('mailto:', '').strip())
        
        return ', '.join(contact_info) if contact_info else "Not available"

    def extract_keyword_sentences(self, soup, keywords):
        """Helper function to extract sentences containing specific keywords."""
        sentences = []
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text()
            if any(keyword in text.lower() for keyword in keywords):
                sentences.append(text.strip())
        
        return sentences if sentences else ["Not available"]

    def generate_summary(self, content: dict, additional_info: dict):
        """Generate a summary using an LLM based on scraped content and details. Explains the company overview, target, innovations, etc. Also who is customer and what is the company's goal?"""
        if not self.summarizer:
            print("Summarizer model is not available.")
            return "No summary available."

        prompt = f"""
        Company Overview: {content['description']}. 
        Year Founded: {additional_info['year_founded']}. 
        Goals: {'; '.join(additional_info['goals'])}. 
        Objectives: {'; '.join(additional_info['objectives'])}. 
        Innovations: {'; '.join(additional_info['innovations'])}. 
        Contact Information: {additional_info['contact_info']}.
        """
        
        try:
            summary = self.summarizer(prompt, max_length=200)[0]['summary_text']
            return summary
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return prompt  # Fallback to raw prompt if summarization fails

    def generate_report(self, analysis: dict, output_path: str):
        """Generate a PDF report based on analysis data."""
        pdf = FPDF()
        
        # Add fonts (assuming Arial is available as per previous setup)
        pdf.add_font('Arial', '', os.path.join('fonts', 'Arial.ttf'), uni=True)
        
        pdf.add_page()

        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f"Prospect Research: {analysis['company_name']}", ln=True)

        # Summary Section
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, f"Summary:\n{analysis['summary']}")

        # Additional Information Section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Additional Information:", ln=True)

        pdf.set_font('Arial', '', 12)
        
        # Year Founded
        pdf.multi_cell(0, 10, f"Year Founded: {analysis['year_founded']}")

        # Goals
        pdf.multi_cell(0, 10, f"Goals:\n{'; '.join(analysis['goals'])}")

        # Objectives
        pdf.multi_cell(0, 10, f"Objectives:\n{'; '.join(analysis['objectives'])}")

        # Innovations
        pdf.multi_cell(0, 10, f"Innovations:\n{'; '.join(analysis['innovations'])}")

        # Contact Information
        pdf.multi_cell(0, 10, f"Contact Information: {analysis['contact_info']}")

        pdf.output(output_path)

    def research_prospect(self, url: str, output_path: str):
        """Main function to orchestrate scraping and report generation."""
        
        content_data, additional_data = self.scrape_website(url)
        
        if not content_data or not additional_data:
            print("Failed to retrieve necessary data.")
            return
        
        analysis_data = {
           "company_name": content_data["title"] or "Unknown Company",
           "summary": self.generate_summary(content_data, additional_data),
           "year_founded": additional_data["year_founded"],
           "goals": additional_data["goals"],
           "objectives": additional_data["objectives"],
           "innovations": additional_data["innovations"],
           "contact_info": additional_data["contact_info"]
       }

        # Generate PDF report
        self.generate_report(analysis_data, output_path)
        print(f"Prospect research report generated at {output_path}")

# Example usage of the class
if __name__ == "__main__":
    researcher = AIProspectResearcher()
    website_url = "https://viso.ai"  # Replace with target website URL.
    output_pdf_path = "prospect_research_report.pdf"
    
    researcher.research_prospect(website_url, output_pdf_path)