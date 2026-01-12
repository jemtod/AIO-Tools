"""
Dork Scanner Tool Module
Handles Google dorking and vulnerability scanning with multiple search engines
"""

import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import requests
import time
from urllib.parse import urljoin, quote_plus
from .progress_logger import ProgressLogger, LogLevel

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None


class DorkScanner:
    """Dork scanner and vulnerability finder with multiple search engines"""
    
    def __init__(self, search_engine='duckduckgo'):
        self.scan_results = []
        self.dork_list = []
        self.vulnerable_urls = []
        self.collected_urls = []
        self.logger = ProgressLogger()
        self.proxies: Optional[Dict[str, str]] = None
        self.search_engine = search_engine  # 'duckduckgo' or 'bing'
    
    def set_search_engine(self, engine: str) -> None:
        """Set search engine: 'duckduckgo', 'bing', or 'both'"""
        if engine.lower() in ['duckduckgo', 'bing', 'both']:
            self.search_engine = engine.lower()
        else:
            self.logger.warning(f"Unknown search engine: {engine}, using DuckDuckGo")
            self.search_engine = 'duckduckgo'
    
    def set_proxies(self, http_proxy: str = "", https_proxy: str = "") -> Optional[Dict[str, str]]:
        """Configure HTTP/HTTPS proxies for outbound requests
        Format: host:port:username:password or host:port (no auth)
        """
        proxies: Dict[str, str] = {}
        
        if http_proxy.strip():
            proxies['http'] = self._parse_proxy(http_proxy.strip())
        if https_proxy.strip():
            proxies['https'] = self._parse_proxy(https_proxy.strip())
        
        self.proxies = proxies if proxies else None
        return self.proxies
    
    def _parse_proxy(self, proxy_str: str) -> str:
        """Parse proxy format: host:port:user:pass -> http://user:pass@host:port"""
        parts = proxy_str.split(':')
        
        if len(parts) == 2:
            # host:port (no authentication)
            host, port = parts
            return f"http://{host}:{port}"
        elif len(parts) == 4:
            # host:port:user:pass
            host, port, user, password = parts
            return f"http://{user}:{password}@{host}:{port}"
        else:
            # Return as-is if format is not recognized
            return proxy_str
    
    # ==================== Dork List Parsing ====================
    def load_dork_file(self, filepath: str) -> Tuple[bool, int]:
        """Load dork list from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.dork_list = [line.strip() for line in f if line.strip()]
            return True, len(self.dork_list)
        except Exception as e:
            print(f"Error loading dork file: {e}")
            return False, 0
    
    def add_dork(self, dork: str) -> None:
        """Add single dork to list"""
        if dork.strip() and dork not in self.dork_list:
            self.dork_list.append(dork.strip())
    
    def get_dork_list(self) -> List[str]:
        """Get current dork list"""
        return self.dork_list
    
    def clear_dork_list(self) -> None:
        """Clear dork list"""
        self.dork_list = []
    
    # ==================== Common Google Dorks ====================
    def get_default_dorks(self) -> Dict[str, List[str]]:
        """Get common vulnerability-related dorks"""
        return {
            'sql_injection': [
                'inurl:".php?id="',
                'inurl:".php?page="',
                'inurl:".php?category="',
                'inurl:".php?product="',
                'inurl:".php?search="',
                'inurl:"?id=" filetype:php',
                'inurl:"?user_id=" filetype:php',
                'inurl:"?product_id=" filetype:php',
            ],
            'login_pages': [
                'inurl:login.php',
                'inurl:admin.php',
                'inurl:user.php',
                'inurl:signin',
                'inurl:authenticate',
            ],
            'sensitive_files': [
                'inurl:config.php',
                'inurl:database.php',
                'inurl:settings.php',
                'inurl:.env',
                'filetype:sql',
            ],
            'backup_files': [
                'inurl:.bak',
                'inurl:.backup',
                'inurl:.old',
                'filetype:zip',
                'filetype:rar',
            ]
        }
    
    # ==================== SQL Injection Detection ====================
    def detect_sql_injection_patterns(self, url: str) -> Dict[str, any]:
        """Detect potential SQL injection vulnerabilities in URL"""
        issues = []
        risk_score = 0
        
        # Check for injectable parameters (main indicator)
        injectable_param_patterns = [
            (r'[?&](id|user_id|product_id|post_id|article_id|page_id)=[\d]*', 40),
            (r'[?&](username|email|login|user|admin)=\w*', 35),
            (r'[?&](search|q|query|keyword|search_term)=\w*', 30),
            (r'[?&](file|path|dir|page|content)=\w*', 35),
            (r'[?&](cat|category|type|status|sort|order)=[\d\w]*', 25),
            (r'[?&](\w+)=[\d]+', 20),  # Any numeric parameter (generic)
        ]
        
        has_injectable_param = False
        for pattern, score in injectable_param_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                param_match = re.search(r'[?&](\w+)=', url, re.IGNORECASE)
                if param_match:
                    issues.append(f"Potentially injectable parameter: {param_match.group(1)}")
                    risk_score += score
                    has_injectable_param = True
                    break  # Count only first injectable param
        
        # If has injectable parameter, check for additional risk indicators
        if has_injectable_param:
            # Check for suspicious values or patterns
            suspicious_patterns = [
                (r"'\s*(?:OR|AND)\s*", 25),
                (r'".*(?:OR|AND).*"', 25),
                (r"UNION.*SELECT", 35),
                (r"SLEEP\s*\(", 35),
                (r"--\s*$", 15),
                (r"#\s*$", 15),
            ]
            
            for pattern, score in suspicious_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    issues.append("Suspicious SQL pattern detected")
                    risk_score += score
                    break
        
        # URLs without injectable params get low score but not zero
        if not has_injectable_param:
            # Check if URL has query parameters at all
            if '?' in url:
                issues.append("URL has query parameters")
                risk_score = 15  # Low risk, but not suspicious
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "High"
        elif risk_score >= 50:
            risk_level = "Medium"
        elif risk_score >= 30:
            risk_level = "Low"
        else:
            risk_level = "Very Low"
        
        return {
            'url': url,
            'risk_level': risk_level,
            'risk_score': min(risk_score, 100),
            'issues': issues,
            'timestamp': datetime.now().isoformat(),
            'has_injectable_params': has_injectable_param,
            'pattern_matched': len(issues) > 0
        }
    
    def test_sql_injection_payloads(self, url: str) -> Dict[str, any]:
        """Test SQL injection payloads by injecting into actual parameters"""
        
        # Parse URL to find parameters
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        
        # If no parameters, can't test
        if not params:
            return {
                'url': url,
                'tested_payloads': [],
                'vulnerable': False
            }
        
        # Simple payloads for testing
        payloads = [
            "' OR '1'='1' -- -",
            "' OR 1=1 -- -",
            "1' AND '1'='1",
        ]
        
        tested_payloads = []
        vulnerable = False
        
        try:
            # Get baseline response
            baseline = requests.get(url, timeout=2, proxies=self.proxies)
            baseline_text = baseline.text.lower()
            baseline_length = len(baseline.text)
        except:
            baseline_text = ""
            baseline_length = 0
        
        # Inject payload into first parameter
        for param_name in list(params.keys())[:1]:  # Test first parameter
            original_value = params[param_name][0]
            
            for payload in payloads:
                if vulnerable:
                    break
                
                # Create test parameter
                test_params = params.copy()
                test_params[param_name] = [original_value + payload]
                
                # Reconstruct URL
                test_query = urlencode(test_params, doseq=True)
                test_url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    test_query,
                    parsed.fragment
                ))
                
                try:
                    response = requests.get(test_url, timeout=2, proxies=self.proxies)
                    response_text = response.text.lower()
                    response_length = len(response.text)
                    
                    # Check for SQL errors in response
                    sql_errors = [
                        'sql syntax error',
                        'mysql_fetch_array',
                        'mysql_num_rows',
                        'you have an error in your sql',
                        'syntax error',
                        'database error',
                        'sql.*error',
                        'fatal error',
                        'warning.*mysql',
                    ]
                    
                    has_error = any(
                        re.search(err, response_text, re.IGNORECASE) 
                        for err in sql_errors
                    )
                    
                    # Check for indicators
                    if has_error or response.status_code == 500:
                        # SQL error found
                        vulnerable = True
                        tested_payloads.append({
                            'payload': payload,
                            'vulnerable': True,
                            'reason': 'SQL error in response',
                            'param': param_name
                        })
                    elif response.status_code == 200 and response_length != baseline_length and abs(response_length - baseline_length) > 50:
                        # Content changed significantly
                        vulnerable = True
                        tested_payloads.append({
                            'payload': payload,
                            'vulnerable': True,
                            'reason': 'Response content changed',
                            'param': param_name,
                            'length_diff': response_length - baseline_length
                        })
                    else:
                        tested_payloads.append({
                            'payload': payload,
                            'vulnerable': False,
                            'reason': 'No SQL error',
                            'param': param_name
                        })
                        
                except requests.Timeout:
                    # Timeout = possible time-based injection
                    vulnerable = True
                    tested_payloads.append({
                        'payload': payload,
                        'vulnerable': True,
                        'reason': 'Request timeout (time-based SQLi)',
                        'param': param_name
                    })
                except Exception as e:
                    pass
        
        return {
            'url': url,
            'tested_payloads': tested_payloads,
            'vulnerable': vulnerable
        }
    
    def check_sql_errors(self, url: str) -> Dict[str, any]:
        """Check for SQL error messages in initial response"""
        try:
            response = requests.get(url, timeout=2, proxies=self.proxies)
            content = response.text.lower()
            response_code = response.status_code
            
            # Comprehensive SQL error patterns
            sql_errors = [
                # MySQL
                r"you have an error in your sql syntax",
                r"mysql_fetch_array\(\)",
                r"mysql_num_rows\(\)",
                r"mysql_error\(\)",
                r"mysql.*error",
                # Generic SQL
                r"sql syntax error",
                r"sql.*error",
                r"syntax error.*near",
                # PostgreSQL
                r"postgresql.*error",
                r"pg_query\(\)",
                # Oracle
                r"oracle.*error|ora-\d{5}",
                # MSSQL
                r"mssql.*error|sql server",
                # SQLite
                r"sqlite.*error",
                # Generic database
                r"database error",
                r"fatal error",
                r"sqlstate\[",
                r"query.*error",
                r"access denied",
                r"warning.*mysql",
            ]
            
            found_errors = []
            for pattern in sql_errors:
                if re.search(pattern, content, re.IGNORECASE):
                    found_errors.append(pattern)
            
            return {
                'url': url,
                'has_sql_errors': len(found_errors) > 0,
                'error_patterns': found_errors,
                'response_code': response_code,
                'error_count': len(found_errors),
                'content_length': len(response.text)
            }
        except Exception:
            return {
                'url': url,
                'has_sql_errors': False,
                'error_patterns': []
            }
    
    # ==================== URL Collection ====================
    def add_vulnerable_url(self, url: str, vulnerability_type: str, severity: str) -> None:
        """Add URL to vulnerable list"""
        record = {
            'url': url,
            'type': vulnerability_type,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'analysis': self.detect_sql_injection_patterns(url)
        }
        self.vulnerable_urls.append(record)
    
    def get_vulnerable_urls(self) -> List[Dict]:
        """Get list of vulnerable URLs"""
        return self.vulnerable_urls
    
    def export_vulnerable_urls(self, filepath: str, format_type: str = 'txt') -> bool:
        """Export vulnerable URLs to file"""
        try:
            if format_type == 'txt':
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("Vulnerable URLs Report\n")
                    f.write("=" * 50 + "\n\n")
                    for record in self.vulnerable_urls:
                        f.write(f"URL: {record['url']}\n")
                        f.write(f"Type: {record['type']}\n")
                        f.write(f"Severity: {record['severity']}\n")
                        f.write(f"Timestamp: {record['timestamp']}\n")
                        f.write(f"Risk Level: {record['analysis']['risk_level']}\n")
                        f.write(f"Issues: {', '.join(record['analysis']['issues'])}\n")
                        f.write("-" * 50 + "\n\n")
            
            elif format_type == 'csv':
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['url', 'type', 'severity', 'risk_level', 'timestamp'])
                    writer.writeheader()
                    for record in self.vulnerable_urls:
                        writer.writerow({
                            'url': record['url'],
                            'type': record['type'],
                            'severity': record['severity'],
                            'risk_level': record['analysis']['risk_level'],
                            'timestamp': record['timestamp']
                        })
            
            return True
        except Exception as e:
            print(f"Error exporting URLs: {e}")
            return False
    
    def clear_vulnerable_urls(self) -> None:
        """Clear vulnerable URLs list"""
        self.vulnerable_urls = []
    
    # ==================== Dork Analysis ====================
    def analyze_dork_list(self) -> Dict[str, any]:
        """Analyze current dork list"""
        if not self.dork_list:
            return {'count': 0, 'types': {}}
        
        types = {
            'parameter_dorks': len([d for d in self.dork_list if 'inurl:' in d and '=' in d]),
            'file_dorks': len([d for d in self.dork_list if 'filetype:' in d]),
            'directory_dorks': len([d for d in self.dork_list if 'inurl:' in d and '/' in d]),
            'other': len([d for d in self.dork_list if 'inurl:' not in d and 'filetype:' not in d])
        }
        
        return {
            'total_dorks': len(self.dork_list),
            'types': types,
            'sample_dorks': self.dork_list[:5]
        }
    
    def get_scan_history(self) -> List[Dict]:
        """Get scan history"""
        return self.scan_results
    
    # ==================== Search Engine Methods ====================
    def _search_bing(self, query: str, max_results: int = 10) -> List[str]:
        """Search using Bing with improved URL extraction"""
        urls = []
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Bing search URL with first parameter for pagination
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}&first=1&count={max_results}"
            
            response = requests.get(search_url, headers=headers, timeout=15, proxies=self.proxies, allow_redirects=True)
            
            if response.status_code == 200:
                content = response.text
                
                # Multiple extraction methods for better results
                
                # Method 1: Extract from cite tags (most reliable)
                cite_pattern = r'<cite[^>]*>([^<]+)</cite>'
                cite_matches = re.findall(cite_pattern, content)
                for match in cite_matches:
                    url = match.strip()
                    # Reconstruct full URL if needed
                    if not url.startswith('http'):
                        url = 'https://' + url
                    if url not in urls:
                        urls.append(url)
                
                # Method 2: Extract from data-bm attribute (Bing's URL storage)
                data_bm_pattern = r'data-bm="(\d+)"[^>]*><h2><a[^>]+href="([^"]+)"'
                bm_matches = re.findall(data_bm_pattern, content)
                for _, url in bm_matches:
                    if url.startswith('http') and url not in urls:
                        urls.append(url)
                
                # Method 3: Look for result links in li.b_algo
                algo_pattern = r'<li class="b_algo"[^>]*>.*?<h2><a[^>]+href="([^"]+)"'
                algo_matches = re.findall(algo_pattern, content, re.DOTALL)
                for url in algo_matches:
                    if url.startswith('http') and 'bing.com' not in url and url not in urls:
                        urls.append(url)
                
                # Method 4: Generic href extraction (fallback)
                if len(urls) < max_results // 2:
                    href_pattern = r'href="(https?://[^"]+)"'
                    href_matches = re.findall(href_pattern, content)
                    for url in href_matches:
                        # Filter out Bing/Microsoft URLs
                        if all(domain not in url.lower() for domain in ['bing.com', 'microsoft.com', 'msn.com', 'live.com']):
                            if url not in urls:
                                urls.append(url)
                                if len(urls) >= max_results:
                                    break
                
                # Limit results
                urls = urls[:max_results]
                
            else:
                self.logger.warning(f"Bing returned status code: {response.status_code}")
            
            time.sleep(2)  # Rate limiting (increased to avoid throttling)
            return urls
            
        except Exception as e:
            self.logger.warning(f"Bing search error: {str(e)}")
            return urls
    
    def _search_duckduckgo(self, query: str, max_results: int = 10) -> List[str]:
        """Search using DuckDuckGo"""
        urls = []
        try:
            if DDGS is None:
                self.logger.error('ddgs library not installed')
                return urls
            
            ddgs = DDGS()
            search_results = ddgs.text(query, max_results=max_results, proxy=self.proxies.get('https') if self.proxies else None)
            
            for result in search_results:
                url = result.get('href', '')
                if url:
                    urls.append(url)
                if len(urls) >= max_results:
                    break
            
            return urls
        except Exception as e:
            self.logger.warning(f"DuckDuckGo search error: {str(e)}")
            return urls
    
    def _search(self, query: str, max_results: int = 10) -> List[str]:
        """Search using selected search engine"""
        if self.search_engine == 'both':
            # Use both search engines and combine results
            urls_ddg = self._search_duckduckgo(query, max_results)
            urls_bing = self._search_bing(query, max_results)
            
            # Combine and deduplicate
            all_urls = []
            seen = set()
            for url in urls_ddg + urls_bing:
                if url not in seen:
                    all_urls.append(url)
                    seen.add(url)
                if len(all_urls) >= max_results * 2:  # Allow more results when using both
                    break
            
            return all_urls
        elif self.search_engine == 'bing':
            return self._search_bing(query, max_results)
        else:
            return self._search_duckduckgo(query, max_results)
    
    # ==================== Google Dorking ====================
    def scan_dorks_google(self, dorks: List[str] = None, max_results: int = 5) -> Dict[str, List[str]]:
        """Scan using selected search engine to collect URLs"""
        try:
            if dorks is None:
                dorks = self.dork_list
            
            if not dorks:
                self.logger.error('No dorks provided')
                return {'error': 'No dorks provided', 'urls': {}}
            
            self.logger.set_total(len(dorks))
            results = {}
            
            for i, dork in enumerate(dorks):
                engine_display = "BOTH (DDG+Bing)" if self.search_engine == 'both' else self.search_engine.upper()
                self.logger.info(f"Scanning dork {i+1}/{len(dorks)}: {dork} [{engine_display}]")
                try:
                    urls = self._search(dork, max_results)
                    
                    # Remove duplicates
                    unique_urls = []
                    for url in urls:
                        if url not in unique_urls and url not in self.collected_urls:
                            unique_urls.append(url)
                            self.collected_urls.append(url)
                    
                    results[dork] = unique_urls
                    self.logger.update_progress(i+1, f"Found {len(unique_urls)} URLs from: {dork}")
                    
                except Exception as e:
                    self.logger.warning(f"Error scanning '{dork}': {str(e)}")
                    results[dork] = []
            
            engine_display = "BOTH (DDG+Bing)" if self.search_engine == 'both' else self.search_engine.upper()
            self.logger.complete(f"Scan complete! Collected {len(self.collected_urls)} total URLs via {engine_display}")
            return results
        except Exception as e:
            self.logger.error(f"Scan error: {str(e)}")
            return {'error': str(e), 'urls': {}}
    
    def scan_single_dork(self, dork: str, max_results: int = 10) -> List[str]:
        """Scan single dork and return URLs"""
        try:
            engine_display = "BOTH (DDG+Bing)" if self.search_engine == 'both' else self.search_engine.upper()
            self.logger.info(f"Scanning single dork: {dork} [{engine_display}]")
            urls = self._search(dork, max_results)
            
            # Remove duplicates and add to collected URLs
            unique_urls = []
            for url in urls:
                if url not in unique_urls and url not in self.collected_urls:
                    unique_urls.append(url)
                    self.collected_urls.append(url)
            
            self.logger.success(f"Found {len(unique_urls)} URLs via {engine_display}")
            return unique_urls
        except Exception as e:
            self.logger.error(f"Error scanning dork: {str(e)}")
            return []
    
    def get_collected_urls(self) -> List[str]:
        """Get all collected URLs"""
        return list(set(self.collected_urls))  # Remove duplicates
    
    def clear_collected_urls(self) -> None:
        """Clear collected URLs"""
        self.collected_urls = []
    
    def filter_urls_by_extension(self, urls: List[str], extensions: List[str]) -> List[str]:
        """Filter URLs by file extension"""
        filtered = []
        for url in urls:
            for ext in extensions:
                if url.lower().endswith(ext.lower()):
                    filtered.append(url)
                    break
        return filtered
    
    def filter_urls_by_pattern(self, urls: List[str], pattern: str) -> List[str]:
        """Filter URLs by regex pattern"""
        try:
            filtered = []
            for url in urls:
                if re.search(pattern, url, re.IGNORECASE):
                    filtered.append(url)
            return filtered
        except Exception as e:
            print(f"Error filtering URLs: {e}")
            return urls
