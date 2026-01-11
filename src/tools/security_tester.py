"""
Security Testing Tool Module
Provides various security testing capabilities
"""

import socket
import hashlib
import hmac
import re
import ssl
import requests
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class SecurityTester:
    """Main security testing tool class"""
    
    def __init__(self):
        self.scan_results = []
        
    # ==================== Port Scanning ====================
    def scan_ports(self, host: str, port_range: Tuple[int, int]) -> Dict[int, bool]:
        """Scan ports on a target host"""
        open_ports = {}
        start_port, end_port = port_range
        
        for port in range(start_port, end_port + 1):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                open_ports[port] = (result == 0)
                sock.close()
            except Exception as e:
                print(f"Error scanning port {port}: {e}")
                open_ports[port] = False
        
        return open_ports
    
    def scan_common_ports(self, host: str) -> Dict[int, str]:
        """Scan common ports"""
        common_ports = {
            21: "FTP",
            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            27017: "MongoDB",
            3389: "RDP",
            5900: "VNC"
        }
        
        results = {}
        for port, service in common_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                results[port] = service if result == 0 else "Closed"
                sock.close()
            except Exception:
                results[port] = "Error"
        
        return results
    
    # ==================== Hash Generation ====================
    def generate_hash(self, text: str, algorithm: str = 'md5') -> str:
        """Generate hash of text"""
        algorithm = algorithm.lower()
        if algorithm == 'md5':
            return hashlib.md5(text.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(text.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(text.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(text.encode()).hexdigest()
        else:
            return ""
    
    def verify_hash(self, text: str, hash_value: str) -> Dict[str, bool]:
        """Verify hash against text"""
        algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        results = {}
        
        for algo in algorithms:
            generated = self.generate_hash(text, algo)
            results[algo] = generated == hash_value.lower()
        
        return results
    
    # ==================== Password Analysis ====================
    def check_password_strength(self, password: str) -> Dict[str, any]:
        """Analyze password strength"""
        strength_score = 0
        issues = []
        
        # Length check
        if len(password) >= 8:
            strength_score += 1
        else:
            issues.append("Password too short (min 8 characters)")
        
        if len(password) >= 12:
            strength_score += 1
        
        # Uppercase
        if re.search(r'[A-Z]', password):
            strength_score += 1
        else:
            issues.append("Missing uppercase letters")
        
        # Lowercase
        if re.search(r'[a-z]', password):
            strength_score += 1
        else:
            issues.append("Missing lowercase letters")
        
        # Numbers
        if re.search(r'\d', password):
            strength_score += 1
        else:
            issues.append("Missing numbers")
        
        # Special characters
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            strength_score += 1
        else:
            issues.append("Missing special characters")
        
        # Determine strength level
        if strength_score >= 6:
            strength = "Strong"
        elif strength_score >= 4:
            strength = "Medium"
        else:
            strength = "Weak"
        
        return {
            'strength': strength,
            'score': strength_score,
            'max_score': 6,
            'issues': issues
        }
    
    def check_common_passwords(self, password: str) -> bool:
        """Check if password is in common passwords list"""
        common_passwords = [
            'password', '123456', '12345678', 'qwerty', 'abc123',
            'password123', '111111', '1234567', 'letmein', 'welcome',
            'monkey', '1234567890', 'admin', 'dragon', 'master'
        ]
        return password.lower() in common_passwords
    
    # ==================== SSL/TLS Check ====================
    def check_ssl_certificate(self, host: str, port: int = 443) -> Dict[str, any]:
        """Check SSL/TLS certificate information"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        'valid': True,
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'version': cert.get('version'),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'serial_number': cert.get('serialNumber')
                    }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    # ==================== Web Security ====================
    def check_security_headers(self, url: str) -> Dict[str, Optional[str]]:
        """Check web security headers"""
        try:
            response = requests.head(url, timeout=5)
            headers = response.headers
            
            security_headers = {
                'Content-Security-Policy': headers.get('Content-Security-Policy'),
                'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
                'X-Frame-Options': headers.get('X-Frame-Options'),
                'X-XSS-Protection': headers.get('X-XSS-Protection'),
                'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
                'Referrer-Policy': headers.get('Referrer-Policy')
            }
            
            return security_headers
        except Exception as e:
            return {'error': str(e)}
    
    def check_http_redirect(self, url: str) -> List[Dict]:
        """Check HTTP redirects"""
        try:
            redirects = []
            response = requests.get(url, allow_redirects=False, timeout=5)
            
            current_url = url
            while response.status_code in [301, 302, 303, 307, 308]:
                redirect_url = response.headers.get('Location')
                redirects.append({
                    'from': current_url,
                    'to': redirect_url,
                    'status_code': response.status_code
                })
                current_url = redirect_url
                response = requests.get(redirect_url, allow_redirects=False, timeout=5)
            
            return redirects
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_scan_history(self) -> List[Dict]:
        """Get history of security scans"""
        return self.scan_results
