import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from urllib.parse import urljoin, urlparse

import pdfkit
import requests
from bs4 import BeautifulSoup

WKHTMLTOPDF_PATH = r"D:\soft\wkhtmltopdf\bin\wkhtmltopdf.exe"

EXCLUDE_PATHS = [
    "/doc/codewalk/",
    "/doc/tutorial/",
]


class WebToPDF:
    def __init__(self, base_url: str, output_dir: str = "output", max_depth: int = 2, 
                 max_pages: int = 0, max_workers: int = 50, wkhtmltopdf_path: str = None, 
                 path_prefix: str = None, exclude_paths: list[str] = None):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.max_workers = max_workers
        self.visited_urls: set[str] = set()
        self.visited_lock = Lock()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.wkhtmltopdf_path = wkhtmltopdf_path or WKHTMLTOPDF_PATH
        self.pdfkit_config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
        if path_prefix:
            self.path_prefix = path_prefix if path_prefix.startswith("/") else f"/{path_prefix}"
        else:
            base_path = urlparse(base_url).path
            self.path_prefix = base_path.rstrip("/") if base_path else ""
        self.exclude_paths = exclude_paths if exclude_paths is not None else EXCLUDE_PATHS

    def sanitize_filename(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            path = "index"
        path = path.replace("/", "_")
        path = re.sub(r'[<>:"/\\|?*]', "_", path)
        path = re.sub(r'_+', "_", path)
        return f"{path}.pdf"

    def is_same_domain(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain

    def is_valid_path(self, url: str) -> bool:
        if not self.path_prefix:
            return True
        parsed = urlparse(url)
        return parsed.path.startswith(self.path_prefix)

    def is_excluded_path(self, url: str) -> bool:
        if not self.exclude_paths:
            return False
        parsed = urlparse(url)
        for exclude_path in self.exclude_paths:
            if parsed.path.startswith(exclude_path):
                return True
        return False

    def normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.path.endswith("/"):
            normalized = normalized[:-1]
        return normalized

    def extract_links(self, html: str, current_url: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        unique_links = set()
        for link in links:
            href = link["href"]
            if href.startswith("#") or href.startswith("javascript:"):
                continue
            absolute_url = urljoin(current_url, href)
            absolute_url = self.normalize_url(absolute_url)
            with self.visited_lock:
                if (self.is_same_domain(absolute_url) and 
                    self.is_valid_path(absolute_url) and 
                    not self.is_excluded_path(absolute_url) and
                    absolute_url not in self.visited_urls):
                    unique_links.add(absolute_url)
        return list(unique_links)

    def crawl_links(self) -> list[str]:
        print("=== 阶段1: 爬取所有链接 ===")
        url_queue = [(self.normalize_url(self.base_url), 0)]
        all_urls = []

        while url_queue:
            current_url, depth = url_queue.pop(0)

            with self.visited_lock:
                if current_url in self.visited_urls:
                    continue
                self.visited_urls.add(current_url)

            if depth > self.max_depth:
                continue

            all_urls.append(current_url)
            print(f"[爬取] 深度 {depth}: {current_url} (已收集 {len(all_urls)} 个)")

            if self.max_pages > 0 and len(all_urls) >= self.max_pages:
                print(f"\n已达到最大页面限制 ({self.max_pages})，停止爬取")
                break

            if depth < self.max_depth:
                try:
                    response = self.session.get(current_url, timeout=30)
                    response.raise_for_status()
                    links = self.extract_links(response.text, current_url)
                    for link in links:
                        with self.visited_lock:
                            if link not in self.visited_urls:
                                url_queue.append((link, depth + 1))
                except Exception as e:
                    print(f"    爬取错误: {e}")

        if self.max_pages > 0:
            all_urls = all_urls[:self.max_pages]

        print(f"\n共收集 {len(all_urls)} 个页面链接\n")
        return all_urls

    def save_page_as_pdf(self, url: str) -> tuple[str, str]:
        filename = self.sanitize_filename(url)
        filepath = self.output_dir / filename
        css_path = Path(__file__).parent / "hide_header.css"
        options = {
            "page-size": "A4",
            "margin-top": "20mm",
            "margin-bottom": "20mm",
            "margin-left": "15mm",
            "margin-right": "15mm",
            "encoding": "UTF-8",
            "enable-local-file-access": None,
            "print-media-type": None,
            "quiet": "",
            "user-style-sheet": str(css_path),
            "outline": None,
            "outline-depth": "3",
            "load-error-handling": "ignore",
            "load-media-error-handling": "ignore",
        }
        pdfkit.from_url(url, str(filepath), options=options, configuration=self.pdfkit_config)
        return url, filename

    def run(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.path_prefix:
            print(f"路径过滤: 只爬取 {self.path_prefix} 开头的页面")
        if self.exclude_paths:
            print(f"排除路径: {', '.join(self.exclude_paths)}")
        if self.max_pages > 0:
            print(f"页面限制: 最多处理 {self.max_pages} 个页面")
        print(f"线程池大小: {self.max_workers}\n")

        all_urls = self.crawl_links()

        print("=== 阶段2: 多线程生成 PDF ===")
        results = []
        success_count = 0
        error_count = 0
        total = len(all_urls)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.save_page_as_pdf, url): url for url in all_urls}
            
            for future in as_completed(futures):
                url = futures[future]
                try:
                    result_url, filename = future.result()
                    success_count += 1
                    print(f"[{success_count}/{total}] 完成: {filename}")
                    results.append((result_url, filename))
                except Exception as e:
                    error_count += 1
                    print(f"[错误] {url}: {e}")

        print(f"\n完成! 成功: {success_count}, 失败: {error_count}")
        print(f"输出目录: {self.output_dir.absolute()}")
        return results


def main():
    if len(sys.argv) < 2:
        print("用法: python web_to_pdf.py <URL> [最大深度] [输出目录] [最大页面数] [线程数]")
        print("示例: python web_to_pdf.py https://go.dev/doc/ 2 output 5 50")
        print("      python web_to_pdf.py https://go.dev/doc/ 2 output 0 50  # 0 表示不限制页面数")
        sys.exit(1)

    url = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
    max_pages = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    max_workers = int(sys.argv[5]) if len(sys.argv) > 5 else 50

    converter = WebToPDF(url, output_dir, max_depth, max_pages, max_workers)
    converter.run()


if __name__ == "__main__":
    main()
