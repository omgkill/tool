import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Optional

from parser_service.crawler.link_extractor import LinkExtractor


@dataclass
class SpiderConfig:
    allowed_domains: list
    max_depth: int = 2
    max_pages: int = 50
    delay: float = 0.1
    url_pattern: Optional[str] = None
    max_workers: int = 100


@dataclass
class DocumentData:
    doc_id: int
    url: str
    title: str
    depth: int
    html: str = ""
    paragraphs: list = field(default_factory=list)
    unique_words: list = field(default_factory=list)
    word_count: int = 0


@dataclass
class SiteData:
    source_url: str
    metadata: dict
    documents: list = field(default_factory=list)
    global_unique_words: list = field(default_factory=list)
    global_word_frequency: dict = field(default_factory=dict)


class Spider:
    def __init__(self, config: SpiderConfig, fetcher, extractor, cleaner, splitter, lemmatizer):
        self.config = config
        self.fetcher = fetcher
        self.extractor = extractor
        self.cleaner = cleaner
        self.splitter = splitter
        self.lemmatizer = lemmatizer
    
    def crawl(self, start_url: str) -> SiteData:
        print(f"[Spider] 开始爬取: {start_url}")
        print(f"[Spider] 配置: max_depth={self.config.max_depth}, max_pages={self.config.max_pages}, max_workers={self.config.max_workers}")
        
        link_extractor = LinkExtractor(
            base_url=start_url,
            allowed_domains=self.config.allowed_domains
        )
        
        # 第一步：先爬取根页面，提取所有文档链接
        print(f"[Spider] 步骤1: 爬取根页面，提取文档链接")
        doc_links = self._extract_all_doc_links(start_url, link_extractor)
        print(f"[Spider] 共发现 {len(doc_links)} 个文档链接")
        
        # 第二步：准备所有待处理的URL列表
        urls_to_process = []
        for i, link in enumerate(doc_links):
            if i >= self.config.max_pages:
                break
            urls_to_process.append((link['url'], 1, i + 1))
        
        print(f"[Spider] 步骤2: 准备处理 {len(urls_to_process)} 个URL")
        
        # 第三步：使用线程池并行处理所有URL
        print(f"[Spider] 步骤3: 开始并行处理URL (worker数: {self.config.max_workers})")
        documents = []
        documents_lock = threading.Lock()
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = []
            
            # 一次性提交所有任务
            for url, depth, doc_id in urls_to_process:
                future = executor.submit(
                    self._process_single_document,
                    url, depth, doc_id
                )
                futures.append(future)
            
            # 收集结果
            completed_count = 0
            for future in as_completed(futures):
                completed_count += 1
                try:
                    result = future.result()
                    if result:
                        with documents_lock:
                            documents.append(result)
                    print(f"[Spider] 进度: {completed_count}/{len(futures)} 完成")
                except Exception as e:
                    print(f"[Spider] 处理任务错误: {e}")
        
        # 第四步：聚合结果
        print(f"[Spider] 步骤4: 聚合结果")
        global_words, global_freq = self._aggregate_words(documents)
        
        site_data = SiteData(
            source_url=start_url,
            metadata={
                'source_url': start_url,
                'crawled_at': self._get_timestamp(),
                'total_documents': len(documents),
                'total_unique_words': len(global_words),
                'config': {
                    'max_depth': self.config.max_depth,
                    'max_pages': self.config.max_pages,
                    'allowed_domains': self.config.allowed_domains,
                    'max_workers': self.config.max_workers
                }
            },
            documents=documents,
            global_unique_words=global_words,
            global_word_frequency=global_freq
        )
        
        print(f"[Spider] 爬取完成: {len(documents)} 个文档")
        return site_data
    
    def _extract_all_doc_links(self, start_url, link_extractor):
        """提取所有文档链接"""
        try:
            html = self.fetcher.fetch(start_url)
            doc_links = link_extractor.extract_document_links(
                html, start_url, self.config.url_pattern
            )
            return doc_links
        except Exception as e:
            print(f"[Spider] 提取文档链接错误: {e}")
            return []
    
    def _process_single_document(self, url, depth, doc_id):
        """处理单个文档：抓取->解析->生成"""
        thread_id = threading.get_ident()
        print(f"[Spider] [线程-{thread_id}] 开始处理 [{doc_id}]: {url}")
        
        try:
            # 1. 抓取
            html = self.fetcher.fetch(url)
            
            # 2. 解析和生成
            text = self.extractor.extract(html)
            cleaned = self.cleaner.clean(text)
            paragraphs = self.splitter.split_paragraphs(cleaned)
            
            if paragraphs:
                paragraphs_data = self.lemmatizer.process_text(paragraphs)
                unique_words = self.lemmatizer.extract_unique_words(paragraphs_data)
                
                title = self._extract_title(html, url)
                
                doc = DocumentData(
                    doc_id=doc_id,
                    url=url,
                    title=title,
                    depth=depth,
                    html=html,
                    paragraphs=paragraphs_data,
                    unique_words=unique_words,
                    word_count=len(unique_words)
                )
                print(f"[Spider] [线程-{thread_id}] 完成 [{doc_id}]: {url} ({len(unique_words)} 个单词)")
                
                if self.config.delay > 0:
                    time.sleep(self.config.delay)
                
                return doc
        except Exception as e:
            print(f"[Spider] [线程-{thread_id}] 错误 [{doc_id}]: {url} - {e}")
        
        return None
    
    def _extract_title(self, html: str, url: str) -> str:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text(strip=True)
        return url
    
    def _aggregate_words(self, documents: list) -> tuple:
        from collections import Counter
        word_set = set()
        word_counts = Counter()
        
        for doc in documents:
            word_set.update(doc.unique_words)
            for para in doc.paragraphs:
                for sent in para.get('sentences', []):
                    for word in sent.get('words', []):
                        lemma = word.get('lemma', '')
                        if lemma:
                            word_counts[lemma] += 1
        
        return sorted(word_set), dict(word_counts.most_common())
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
