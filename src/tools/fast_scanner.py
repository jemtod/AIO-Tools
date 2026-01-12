"""
Fast Scanner Module - Optimized for Performance
Multi-threaded scanner with connection pooling and batch processing
"""

import re
import time
import requests
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import queue
from .progress_logger import ProgressLogger, LogLevel

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None


class FastScanner:
    """High-performance scanner with multi-threading and connection pooling"""
    
    def __init__(self, max_workers: int = 10, timeout: int = 5, search_engine: str = 'duckduckgo'):
        """
        Initialize fast scanner
        
        Args:
            max_workers: Maximum concurrent threads (default: 10)
            timeout: Request timeout in seconds (default: 5)
            search_engine: Search engine to use (default: 'duckduckgo')
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.logger = ProgressLogger()
        self.proxies: Optional[Dict[str, str]] = None
        self.search_engine = search_engine.lower()
        
        # Thread-safe data structures
        self._lock = Lock()
        self.collected_urls: Set[str] = set()
        self.vulnerable_urls: List[Dict] = []
        
        # Session pool for connection reuse
        self.session_pool = queue.Queue(maxsize=max_workers)
        for _ in range(max_workers):
            session = self._create_session()
            self.session_pool.put(session)
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with optimized settings"""
        session = requests.Session()
        
        # Connection pooling adapter
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=2,
            pool_block=False
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Default headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        if self.proxies:
            session.proxies.update(self.proxies)
        
        return session
    
    def set_proxies(self, http_proxy: str = "", https_proxy: str = "") -> Optional[Dict[str, str]]:
        """Configure proxies"""
        proxies: Dict[str, str] = {}
        
        if http_proxy.strip():
            proxies['http'] = self._parse_proxy(http_proxy.strip())
        if https_proxy.strip():
            proxies['https'] = self._parse_proxy(https_proxy.strip())
        
        self.proxies = proxies if proxies else None
        
        # Update all sessions in pool
        if self.proxies:
            temp_sessions = []
            while not self.session_pool.empty():
                try:
                    session = self.session_pool.get_nowait()
                    session.proxies.update(self.proxies)
                    temp_sessions.append(session)
                except queue.Empty:
                    break
            
            for session in temp_sessions:
                self.session_pool.put(session)
        
        return self.proxies
    
    def _parse_proxy(self, proxy_str: str) -> str:
        """Parse proxy format"""
        parts = proxy_str.split(':')
        if len(parts) == 2:
            return f"http://{parts[0]}:{parts[1]}"
        elif len(parts) == 4:
            return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        return proxy_str
    
    def _get_session(self) -> requests.Session:
        """Get session from pool with timeout to prevent blocking"""
        try:
            return self.session_pool.get(timeout=2)
        except queue.Empty:
            # Fallback: create new session if pool is exhausted
            return self._create_session()
    
    def _return_session(self, session: requests.Session):
        """Return session to pool with timeout to prevent blocking"""
        try:
            self.session_pool.put(session, timeout=2)
        except queue.Full:
            # Pool is full, close session to free resources
            try:
                session.close()
            except:
                pass
    
    # ==================== Fast Dork Scanning ====================
    
    def scan_dorks_parallel(self, dorks: List[str], max_results_per_dork: int = 10) -> Dict[str, List[str]]:
        """
        Scan multiple dorks in parallel using thread pool
        
        Args:
            dorks: List of dork queries
            max_results_per_dork: Max results per dork
            
        Returns:
            Dict mapping dork to list of found URLs
        """
        if not dorks:
            return {}
        
        if DDGS is None:
            self.logger.error('ddgs library not installed')
            return {}
        
        self.logger.info(f"Starting parallel scan of {len(dorks)} dorks with {self.max_workers} workers")
        start_time = time.time()
        
        results = {}
        completed = 0
        total = len(dorks)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all dork scans
            future_to_dork = {
                executor.submit(self._scan_single_dork_worker, dork, max_results_per_dork): dork
                for dork in dorks
            }
            
            # Process completed tasks
            for future in as_completed(future_to_dork):
                dork = future_to_dork[future]
                try:
                    urls = future.result()
                    results[dork] = urls
                    completed += 1
                    
                    self.logger.update_progress(
                        completed, 
                        f"[{completed}/{total}] {dork}: {len(urls)} URLs"
                    )
                except Exception as e:
                    self.logger.warning(f"Error scanning '{dork}': {str(e)}")
                    results[dork] = []
                    completed += 1
        
        elapsed = time.time() - start_time
        total_urls = sum(len(urls) for urls in results.values())
        
        self.logger.complete(
            f"Parallel scan complete! {total_urls} URLs in {elapsed:.2f}s "
            f"({total_urls/elapsed:.2f} URLs/sec)"
        )
        
        return results
    
    def _scan_single_dork_worker(self, dork: str, max_results: int) -> List[str]:
        """Worker function to scan single dork"""
        try:
            urls = []
            ddgs = DDGS()
            proxy = self.proxies.get('https') if self.proxies else None
            
            search_results = ddgs.text(dork, max_results=max_results, proxy=proxy)
            
            for result in search_results:
                url = result.get('href', '')
                if url:
                    with self._lock:
                        if url not in self.collected_urls:
                            self.collected_urls.add(url)
                            urls.append(url)
                
                if len(urls) >= max_results:
                    break
            
            return urls
        except Exception as e:
            self.logger.debug(f"Dork scan error: {str(e)}")
            return []
    
    # ==================== Fast SQL Injection Scanning ====================
    
    def scan_urls_for_sqli_parallel(self, urls: List[str]) -> Dict[str, Dict]:
        """
        Scan multiple URLs for SQL injection in parallel
        
        Args:
            urls: List of URLs to test
            
        Returns:
            Dict mapping URL to vulnerability info
        """
        if not urls:
            return {}
        
        # Optimize worker count based on URL count (prevent too many threads)
        optimal_workers = min(self.max_workers, max(1, len(urls) // 5))
        self.logger.info(f"Starting parallel SQLi scan of {len(urls)} URLs with {optimal_workers} workers")
        start_time = time.time()
        
        results = {}
        completed = 0
        total = len(urls)
        
        # Use timeout to prevent hanging
        effective_timeout = max(2, self.timeout)
        
        with ThreadPoolExecutor(max_workers=optimal_workers, thread_name_prefix="sqli_scan_") as executor:
            # Submit all URL scans
            future_to_url = {}
            for url in urls:
                try:
                    future = executor.submit(self._scan_url_for_sqli_worker, url)
                    future_to_url[future] = url
                except Exception as e:
                    self.logger.debug(f"Failed to submit scan for {url}: {str(e)}")
                    results[url] = {'vulnerable': False, 'error': str(e)}
                    completed += 1
            
            # Process completed tasks with timeout
            for future in as_completed(future_to_url, timeout=effective_timeout + 10):
                url = future_to_url[future]
                try:
                    result = future.result(timeout=effective_timeout)
                    results[url] = result
                    completed += 1
                    
                    status = "✓ VULNERABLE" if result.get('vulnerable') else "✗ Clean"
                    self.logger.update_progress(
                        completed,
                        f"[{completed}/{total}] {status}: {url[:60]}"
                    )
                    
                    # Store vulnerable URLs
                    if result.get('vulnerable'):
                        with self._lock:
                            self.vulnerable_urls.append(result)
                    
                except Exception as e:
                    self.logger.debug(f"Error scanning {url}: {str(e)}")
                    results[url] = {'vulnerable': False, 'error': str(e)}
                    completed += 1
        
        elapsed = time.time() - start_time
        vulnerable_count = sum(1 for r in results.values() if r.get('vulnerable'))
        
        self.logger.complete(
            f"SQLi scan complete! {vulnerable_count}/{total} vulnerable "
            f"in {elapsed:.2f}s ({total/elapsed:.2f} URLs/sec)"
        )
        
        return results
    
    def _scan_url_for_sqli_worker(self, url: str) -> Dict:
        """Worker function to scan single URL for SQL injection"""
        result = {
            'url': url,
            'vulnerable': False,
            'method': 'Unknown',
            'sql_type': 'None',
            'risk_level': 'Low',
            'details': []
        }
        
        session = self._get_session()
        worker_timeout = max(2, self.timeout)
        
        try:
            # Pattern detection (fast, non-blocking)
            if self._has_sql_patterns(url):
                result['details'].append('SQL patterns detected in URL')
                result['risk_level'] = 'Medium'
            
            # Test SQL error messages with reduced timeout
            if self._test_sql_errors_fast(url, session, worker_timeout):
                result['vulnerable'] = True
                result['method'] = 'Error-based'
                result['sql_type'] = 'MySQL/MSSQL'
                result['risk_level'] = 'High'
                result['details'].append('SQL error messages detected')
            
            # Test basic payloads with reduced timeout
            elif self._test_sql_payloads_fast(url, session, worker_timeout):
                result['vulnerable'] = True
                result['method'] = 'Boolean-based'
                result['sql_type'] = 'Generic'
                result['risk_level'] = 'High'
                result['details'].append('SQL injection confirmed via payloads')
        
        except Exception as e:
            result['details'].append(f'Error: {str(e)}')
        
        finally:
            self._return_session(session)
        
        return result
    
    def _has_sql_patterns(self, url: str) -> bool:
        """Quick check for SQL injection patterns"""
        patterns = [
            r'\?id=\d+',
            r'\?user_id=\d+',
            r'\?product=\d+',
            r'\?category=\d+',
            r'\?page=\d+',
            r'\.php\?.*=\d+'
        ]
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in patterns)
    
    def _test_sql_errors_fast(self, url: str, session: requests.Session, timeout: int = 3) -> bool:
        """Fast SQL error detection with single quotes"""
        try:
            # Inject single quote
            test_url = url + "'" if '?' in url else url + "?id=1'"
            
            response = session.get(test_url, timeout=timeout, allow_redirects=False)
            content = response.text.lower()
            
            # SQL error signatures
            sql_errors = [
                'sql syntax', 'mysql', 'mysqli', 'syntax error',
                'unclosed quotation', 'quoted string', 'warning: mysql',
                'error in your sql', 'mysql_fetch', 'pg_query',
                'postgresql', 'sqlite', 'microsoft sql', 'odbc',
                'jdbc', 'oracle', 'ora-', 'db2 sql', 'sybase'
            ]
            
            return any(error in content for error in sql_errors)
        
        except Exception:
            return False
    
    def _test_sql_payloads_fast(self, url: str, session: requests.Session, timeout: int = 3) -> bool:
        """Fast SQL injection payload testing with timeout protection"""
        try:
            # Get baseline response with timeout
            baseline = session.get(url, timeout=timeout, allow_redirects=False)
            baseline_length = len(baseline.text)
            
            # Test boolean-based SQLi (reduced payloads for speed)
            payloads = [
                "' OR '1'='1",
                "' OR 1=1--",
            ]
            
            for payload in payloads:
                if '?' in url:
                    test_url = url + payload
                else:
                    test_url = url + "?id=" + payload
                
                try:
                    response = session.get(test_url, timeout=timeout, allow_redirects=False)
                    
                    # Check for significant response difference
                    length_diff = abs(len(response.text) - baseline_length)
                    if length_diff > 100:  # Significant difference
                        return True
                
                except Exception:
                    continue
            
            return False
        
        except Exception:
            return False
    
    # ==================== Batch Processing ====================
    
    def process_urls_in_batches(self, urls: List[str], batch_size: int = 50,
                                operation: str = 'sqli') -> Dict:
        """
        Process URLs in batches for memory efficiency
        
        Args:
            urls: List of URLs to process
            batch_size: Size of each batch
            operation: Type of operation ('sqli', 'alive', 'info')
            
        Returns:
            Combined results from all batches
        """
        if not urls:
            return {}
        
        total_batches = (len(urls) + batch_size - 1) // batch_size
        self.logger.info(f"Processing {len(urls)} URLs in {total_batches} batches of {batch_size}")
        
        all_results = {}
        
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} URLs)")
            
            if operation == 'sqli':
                batch_results = self.scan_urls_for_sqli_parallel(batch)
            elif operation == 'alive':
                batch_results = self.check_urls_alive_parallel(batch)
            elif operation == 'info':
                batch_results = self.gather_url_info_parallel(batch)
            else:
                batch_results = {}
            
            all_results.update(batch_results)
            
            # Small delay between batches
            if i + batch_size < len(urls):
                time.sleep(0.5)
        
        return all_results
    
    # ==================== Additional Fast Operations ====================
    
    def check_urls_alive_parallel(self, urls: List[str]) -> Dict[str, bool]:
        """Check if URLs are alive in parallel"""
        if not urls:
            return {}
        
        self.logger.info(f"Checking {len(urls)} URLs alive status")
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self._check_url_alive_worker, url): url
                for url in urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except:
                    results[url] = False
        
        alive_count = sum(1 for v in results.values() if v)
        self.logger.success(f"{alive_count}/{len(urls)} URLs are alive")
        
        return results
    
    def _check_url_alive_worker(self, url: str) -> bool:
        """Check if single URL is alive"""
        session = self._get_session()
        try:
            response = session.head(url, timeout=self.timeout, allow_redirects=True)
            return response.status_code < 400
        except:
            return False
        finally:
            self._return_session(session)
    
    def gather_url_info_parallel(self, urls: List[str]) -> Dict[str, Dict]:
        """Gather basic info from URLs in parallel"""
        if not urls:
            return {}
        
        self.logger.info(f"Gathering info from {len(urls)} URLs")
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self._gather_url_info_worker, url): url
                for url in urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    results[url] = {'error': str(e)}
        
        return results
    
    def _gather_url_info_worker(self, url: str) -> Dict:
        """Gather info from single URL"""
        session = self._get_session()
        info = {
            'url': url,
            'status': 0,
            'server': 'Unknown',
            'content_type': 'Unknown',
            'response_time': 0
        }
        
        try:
            start = time.time()
            response = session.get(url, timeout=self.timeout, allow_redirects=False)
            info['response_time'] = time.time() - start
            info['status'] = response.status_code
            info['server'] = response.headers.get('Server', 'Unknown')
            info['content_type'] = response.headers.get('Content-Type', 'Unknown')
        except Exception as e:
            info['error'] = str(e)
        finally:
            self._return_session(session)
        
        return info
    
    # ==================== Utilities ====================
    
    def get_collected_urls(self) -> List[str]:
        """Get all collected URLs"""
        with self._lock:
            return list(self.collected_urls)
    
    def get_vulnerable_urls(self) -> List[Dict]:
        """Get all vulnerable URLs found"""
        with self._lock:
            return self.vulnerable_urls.copy()
    
    def clear_results(self):
        """Clear all results"""
        with self._lock:
            self.collected_urls.clear()
            self.vulnerable_urls.clear()
    
    def get_statistics(self) -> Dict:
        """Get scanner statistics"""
        with self._lock:
            return {
                'total_urls_collected': len(self.collected_urls),
                'vulnerable_urls': len(self.vulnerable_urls),
                'max_workers': self.max_workers,
                'timeout': self.timeout,
                'sessions_in_pool': self.session_pool.qsize()
            }
    
    def __del__(self):
        """Cleanup sessions on deletion"""
        while not self.session_pool.empty():
            try:
                session = self.session_pool.get_nowait()
                session.close()
            except:
                pass
