# ai-company-insights-tools
 An AI-powered tool that automates prospect research for sales teams by generating concise, insightful articles from a company’s website


## Features

- **Website Scraping**: Extracts the title, meta description, and main content from a given company website.
- **Dynamic Summarization**: Uses an AI-powered summarizer model (based on Facebook’s BART model) to generate a concise overview of the scraped content.
- **Progress Feedback**: Utilizes a progress bar (via `tqdm`) to show summarization progress in real-time for better user experience.
- **PDF Report Generation**: Compiles the title, description, and summarized content into a professional PDF report.


## PREPARING  

Please install requirements.

## USAGE  

### Using `create.py`

The `create.py` script is used to scrape a company's website, summarize the content, and generate a PDF report.

#### Steps to use `create.py`:

1. Open your terminal.
2. Navigate to the directory where `create.py` is located.
3. Run the script with the following command:

```sh
python create.py
```
Only run python file and apply every step in command line...  
1. enter website  
2. If you want create pdf report for write YES or press ENTER for skip