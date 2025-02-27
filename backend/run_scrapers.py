import os
import sys
from scrapers import get_all_scrapers
from processors.document_processor import DocumentProcessor

def main():
    # Set paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    vectorstore_dir = os.path.join(base_dir, "vectorstores")
    
    # Run scrapers
    print("Starting web scraping...")
    scrapers = get_all_scrapers(data_dir)
    for scraper in scrapers:
        print(f"Scraping {scraper.cdp_name}...")
        page_count = scraper.scrape(max_pages=50)  # Limit for testing
        print(f"Scraped {page_count} pages from {scraper.cdp_name}")
    
    # Process documents
    print("\nProcessing documents...")
    processor = DocumentProcessor(data_dir, vectorstore_dir)
    processor.process_all_cdps()
    
    print("\nScraping and processing complete!")

if __name__ == "__main__":
    main()