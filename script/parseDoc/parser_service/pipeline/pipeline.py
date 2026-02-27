from parser_service.fetcher.web_fetcher import WebFetcher
from parser_service.crawler.link_extractor import LinkExtractor
from parser_service.extractor.extractor import Extractor
from parser_service.processor.processor import Processor
from parser_service.output.json_output import JsonOutput
from parser_service.output.txt_output import TxtOutput
from parser_service.output.pdf_output import PdfOutput
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime
import os


class Pipeline:
    def __init__(self, config=None):
        self.config = config or {}
        
        self.default_config = {
            'pipeline': ['crawl', 'extract', 'process', 'output'],
            'output_formats': ['json', 'txt', 'pdf'],
            'nlp_enabled': True,
            'max_pages': 50,
            'max_workers': 100,
            'delay': 0.1,
            'output_dir': 'output'
        }
        
        self.config = {**self.default_config, **self.config}
    
    def run(self, start_url):
        """运行管道"""
        print("=" * 50)
        print("开始管道处理")
        print("=" * 50)
        
        # 创建输出目录
        output_dir = self.config.get('output_dir', 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成带时间戳的输出文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_json = os.path.join(output_dir, f'{timestamp}_output.json')
        output_txt = os.path.join(output_dir, f'{timestamp}_words.txt')
        output_pdf = os.path.join(output_dir, f'{timestamp}_documents.pdf')
        
        fetcher = WebFetcher()
        extractor = Extractor()
        processor = Processor() if self.config.get('nlp_enabled', True) else None
        
        # 步骤1：爬取
        print(f"[Pipeline] 步骤1: 爬取 {start_url}")
        link_extractor = LinkExtractor(base_url=start_url, allowed_domains=[start_url.split('/')[2]])
        html = fetcher.fetch(start_url)
        doc_links = link_extractor.extract_document_links(html, start_url)
        print(f"[Pipeline] 发现 {len(doc_links)} 个文档链接")
        
        # 准备URL列表
        urls_to_crawl = []
        for i, link in enumerate(doc_links):
            if i >= self.config.get('max_pages', 50):
                break
            urls_to_crawl.append((link['url'], 1, i + 1))
        
        # 并行爬取
        documents = []
        documents_lock = threading.Lock()
        
        with ThreadPoolExecutor(max_workers=self.config.get('max_workers', 100)) as executor:
            futures = []
            
            for url, depth, doc_id in urls_to_crawl:
                future = executor.submit(
                    self._process_single_page,
                    url, depth, doc_id, fetcher, extractor, processor
                )
                futures.append(future)
            
            completed_count = 0
            for future in as_completed(futures):
                completed_count += 1
                try:
                    result = future.result()
                    if result:
                        with documents_lock:
                            documents.append(result)
                    print(f"[Pipeline] 进度: {completed_count}/{len(futures)} 完成")
                except Exception as e:
                    print(f"[Pipeline] 处理任务错误: {e}")
        
        # 聚合结果
        print(f"[Pipeline] 步骤2: 聚合结果")
        global_words, global_freq = self._aggregate_words(documents)
        
        # 准备输出数据
        site_data = {
            'source_url': start_url,
            'metadata': {
                'source_url': start_url,
                'crawled_at': datetime.now().isoformat(),
                'total_documents': len(documents),
                'total_unique_words': len(global_words),
            },
            'documents': documents,
            'global_unique_words': global_words,
            'global_word_frequency': global_freq
        }
        
        # 输出
        print(f"[Pipeline] 步骤3: 输出结果")
        if 'json' in self.config.get('output_formats', []):
            JsonOutput().save(site_data, output_json)
        if 'txt' in self.config.get('output_formats', []):
            TxtOutput().save(site_data, output_txt)
        if 'pdf' in self.config.get('output_formats', []):
            PdfOutput().save(site_data, output_pdf)
        
        print("=" * 50)
        print("管道处理完成！")
        print(f"  - 处理文档数: {len(documents)}")
        print(f"  - 唯一单词数: {len(global_words)}")
        print(f"  - 输出目录: {output_dir}/")
        print(f"    - {os.path.basename(output_json)}")
        print(f"    - {os.path.basename(output_txt)}")
        print(f"    - {os.path.basename(output_pdf)}")
        print("=" * 50)
        
        return site_data
    
    def _process_single_page(self, url, depth, doc_id, fetcher, extractor, processor):
        """处理单个页面"""
        thread_id = threading.get_ident()
        print(f"[Pipeline] [线程-{thread_id}] 爬取 [{doc_id}]: {url}")
        
        try:
            # 抓取
            html = fetcher.fetch(url)
            
            # 解析
            text = extractor.extract_text(html)
            title = extractor.extract_title(html)
            
            # NLP处理
            if processor:
                paragraphs = processor.process_text(text)
                unique_words = processor.extract_unique_words(paragraphs)
                word_count = len(unique_words)
            else:
                paragraphs = []
                unique_words = []
                word_count = 0
            
            doc = {
                'doc_id': doc_id,
                'url': url,
                'title': title,
                'depth': depth,
                'html': html,
                'text': text,
                'paragraphs': paragraphs,
                'unique_words': unique_words,
                'word_count': word_count
            }
            
            print(f"[Pipeline] [线程-{thread_id}] 完成 [{doc_id}]: {url} ({word_count} 个单词)")
            
            return doc
        except Exception as e:
            print(f"[Pipeline] [线程-{thread_id}] 错误 [{doc_id}]: {url} - {e}")
            return None
    
    def _aggregate_words(self, documents):
        """聚合单词"""
        from collections import Counter
        word_set = set()
        word_counts = Counter()
        
        for doc in documents:
            word_set.update(doc.get('unique_words', []))
            for para in doc.get('paragraphs', []):
                for sent in para.get('sentences', []):
                    for word in sent.get('words', []):
                        lemma = word.get('lemma', '')
                        if lemma:
                            word_counts[lemma] += 1
        
        return sorted(word_set), dict(word_counts.most_common())