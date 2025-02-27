import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class BaseScraper:
    def __init__(self, base_url, output_dir, cdp_name):
        self.base_url = base_url
        self.output_dir = os.path.join(output_dir, cdp_name)
        self.cdp_name = cdp_name
        self.visited_urls = set()
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def clean_filename(self, url):
        """Convert URL to a valid filename"""
        return url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_') + '.json'
    
    def save_content(self, url, title, content):
        """Save the extracted content to a file"""
        article = {
            'url': url,
            'title': title if title else 'Untitled',
            'content': content,
            'source': self.cdp_name
        }
        
        filename = os.path.join(self.output_dir, self.clean_filename(url))
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        
        print(f"Saved: {url}")
    
    def scrape(self, max_pages=100):
        """Base scrape method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement the scrape method")