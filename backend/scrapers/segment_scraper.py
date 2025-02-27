from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from .base_scraper import BaseScraper

class SegmentScraper(BaseScraper):
    def __init__(self, output_dir):
        super().__init__(
            base_url="https://segment.com/docs/",
            output_dir=output_dir,
            cdp_name="segment"
        )
    
    def extract_content(self, soup):
        """Extract the main content from a Segment docs page"""
        main_content = soup.find('article')
        if not main_content:
            main_content = soup.find('div', class_='main-content')
        
        if main_content:
            # Remove navigation elements
            for nav in main_content.find_all(['nav', 'aside']):
                nav.decompose()
            
            # Return clean text
            return main_content.get_text(separator='\n', strip=True)
        
        return ""
    
    def scrape(self, max_pages=100):
        to_visit = [self.base_url]
        page_count = 0
        
        while to_visit and page_count < max_pages:
            url = to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            try:
                print(f"Scraping: {url}")
                response = requests.get(url)
                self.visited_urls.add(url)
                
                if response.status_code != 200:
                    print(f"Failed to fetch {url}, status code: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string if soup.title else "Untitled"
                content = self.extract_content(soup)
                
                if content:
                    self.save_content(url, title, content)
                    page_count += 1
                
                # Find links to other documentation pages
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/docs/' in href:
                        next_url = urljoin(self.base_url, href)
                        if next_url not in self.visited_urls and next_url not in to_visit:
                            to_visit.append(next_url)
            
            except Exception as e:
                print(f"Error processing {url}: {e}")
        
        print(f"Scraped {page_count} pages from {self.cdp_name}")
        return page_count