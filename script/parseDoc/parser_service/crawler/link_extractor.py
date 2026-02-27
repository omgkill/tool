from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re


class LinkExtractor:
    def __init__(self, base_url: str, allowed_domains: list):
        self.base_url = base_url
        self.allowed_domains = allowed_domains
        self._base_parsed = urlparse(base_url)
    
    def is_same_domain(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return any(allowed in domain for allowed in self.allowed_domains)
        except Exception:
            return False
    
    def normalize_url(self, url: str, current_url: str) -> str:
        if url.startswith('#'):
            return None
        if url.startswith('javascript:'):
            return None
        if url.startswith('mailto:'):
            return None
        if url.startswith('tel:'):
            return None
        
        absolute = urljoin(current_url, url)
        parsed = urlparse(absolute)
        
        if parsed.scheme not in ('http', 'https'):
            return None
        
        return absolute.split('#')[0].rstrip('/')
    
    def extract(self, html: str, current_url: str) -> list:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            normalized = self.normalize_url(href, current_url)
            
            if normalized and self.is_same_domain(normalized):
                links.append(normalized)
        
        return list(set(links))
    
    def extract_document_links(self, html: str, current_url: str, url_pattern: str = None) -> list:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            normalized = self.normalize_url(href, current_url)
            
            if normalized and self.is_same_domain(normalized):
                if url_pattern is None or re.search(url_pattern, normalized):
                    title = a_tag.get_text(strip=True) or normalized
                    links.append({
                        'url': normalized,
                        'title': title
                    })
        
        seen = set()
        unique_links = []
        for link in links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)
        
        return unique_links
