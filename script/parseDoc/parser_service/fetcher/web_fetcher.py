import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time


class WebFetcher:
    def __init__(self, timeout=60, max_retries=3, proxy_port=10809):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        self.proxies = {
            'http': f'http://127.0.0.1:{proxy_port}',
            'https': f'http://127.0.0.1:{proxy_port}'
        }
        self.session = self._create_session(max_retries)
    
    def _create_session(self, max_retries):
        session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def set_proxy(self, http_proxy=None, https_proxy=None):
        if http_proxy:
            self.proxies['http'] = http_proxy
        if https_proxy:
            self.proxies['https'] = https_proxy
    
    def disable_proxy(self):
        self.proxies = {
            'http': None,
            'https': None
        }
    
    def fetch(self, url, retry_count=0):
        print(f"[Fetcher] 正在获取网页: {url}")
        print(f"[Fetcher] 使用代理: {self.proxies['https']}")
        
        try:
            response = self.session.get(
                url,
                headers=self.headers,
                proxies=self.proxies,
                timeout=self.timeout,
                verify=True
            )
            response.raise_for_status()
            print(f"[Fetcher] 获取成功，内容长度: {len(response.text)} 字符")
            return response.text
            
        except requests.exceptions.SSLError as e:
            print(f"[Fetcher] SSL错误: {e}")
            if retry_count < 2:
                print(f"[Fetcher] 尝试禁用SSL验证重试...")
                try:
                    response = self.session.get(
                        url,
                        headers=self.headers,
                        proxies=self.proxies,
                        timeout=self.timeout,
                        verify=False
                    )
                    response.raise_for_status()
                    print(f"[Fetcher] 获取成功（跳过SSL验证），内容长度: {len(response.text)} 字符")
                    return response.text
                except Exception as e2:
                    print(f"[Fetcher] 重试失败: {e2}")
            raise
            
        except requests.exceptions.Timeout as e:
            print(f"[Fetcher] 请求超时: {e}")
            raise
            
        except requests.exceptions.ConnectionError as e:
            print(f"[Fetcher] 连接错误: {e}")
            raise
            
        except Exception as e:
            print(f"[Fetcher] 未知错误: {e}")
            raise
