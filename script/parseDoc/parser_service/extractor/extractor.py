from bs4 import BeautifulSoup


class Extractor:
    def __init__(self):
        self.remove_tags = ['script', 'style', 'nav', 'footer', 'header', 'aside']
    
    def extract_text(self, html):
        """提取文本内容"""
        print("[Extractor] 正在解析HTML...")
        soup = BeautifulSoup(html, 'html.parser')
        
        for tag in self.remove_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', class_='content') or 
            soup.find('body')
        )
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        
        print(f"[Extractor] 提取文本长度: {len(text)} 字符")
        return text
    
    def extract_title(self, html):
        """提取标题"""
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text(strip=True)
        return ""