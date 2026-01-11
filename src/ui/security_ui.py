"""
Security Tester UI Module
PyQt6 interface for security testing tool
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton,
    QLabel, QLineEdit, QComboBox, QTextEdit, QSpinBox, QMessageBox,
    QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from tools import SecurityTester


class SecurityTesterUI(QWidget):
    """Security Tester UI Component"""
    
    def __init__(self):
        super().__init__()
        self.tester = SecurityTester()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Security Testing Tool")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_port_scan_tab(), "Port Scan")
        tabs.addTab(self._create_hash_tab(), "Hash Tools")
        tabs.addTab(self._create_password_tab(), "Password Check")
        tabs.addTab(self._create_ssl_tab(), "SSL/TLS Check")
        tabs.addTab(self._create_security_headers_tab(), "Security Headers")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_port_scan_tab(self):
        """Create port scan tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Target host
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Target Host:"))
        self.scan_host = QLineEdit()
        self.scan_host.setPlaceholderText("e.g., 127.0.0.1 or example.com")
        host_layout.addWidget(self.scan_host)
        layout.addLayout(host_layout)
        
        # Port range
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port Range:"))
        self.port_start = QSpinBox()
        self.port_start.setValue(1)
        self.port_start.setMaximum(65535)
        port_layout.addWidget(self.port_start)
        port_layout.addWidget(QLabel("to"))
        self.port_end = QSpinBox()
        self.port_end.setValue(1024)
        self.port_end.setMaximum(65535)
        port_layout.addWidget(self.port_end)
        layout.addLayout(port_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        scan_btn = QPushButton("Scan Ports")
        scan_btn.clicked.connect(self._scan_ports)
        btn_layout.addWidget(scan_btn)
        
        common_btn = QPushButton("Scan Common Ports")
        common_btn.clicked.connect(self._scan_common_ports)
        btn_layout.addWidget(common_btn)
        layout.addLayout(btn_layout)
        
        # Results
        layout.addWidget(QLabel("Results:"))
        self.scan_results = QTextEdit()
        self.scan_results.setReadOnly(True)
        layout.addWidget(self.scan_results)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_hash_tab(self):
        """Create hash tools tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Hash generation
        layout.addWidget(QLabel("Generate Hash:"))
        
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text:"))
        self.hash_text = QLineEdit()
        text_layout.addWidget(self.hash_text)
        layout.addLayout(text_layout)
        
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Algorithm:"))
        self.hash_algo = QComboBox()
        self.hash_algo.addItems(["MD5", "SHA1", "SHA256", "SHA512"])
        algo_layout.addWidget(self.hash_algo)
        layout.addLayout(algo_layout)
        
        gen_btn = QPushButton("Generate")
        gen_btn.clicked.connect(self._generate_hash)
        layout.addWidget(gen_btn)
        
        layout.addWidget(QLabel("Hash Result:"))
        self.hash_result = QTextEdit()
        self.hash_result.setReadOnly(True)
        self.hash_result.setMaximumHeight(100)
        layout.addWidget(self.hash_result)
        
        # Hash verification
        layout.addWidget(QLabel("Verify Hash:"))
        
        verify_layout = QHBoxLayout()
        verify_layout.addWidget(QLabel("Hash Value:"))
        self.verify_hash = QLineEdit()
        verify_layout.addWidget(self.verify_hash)
        layout.addLayout(verify_layout)
        
        verify_btn = QPushButton("Verify")
        verify_btn.clicked.connect(self._verify_hash)
        layout.addWidget(verify_btn)
        
        self.verify_result = QTextEdit()
        self.verify_result.setReadOnly(True)
        layout.addWidget(self.verify_result)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_password_tab(self):
        """Create password check tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Password input
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_layout.addWidget(self.password_input)
        layout.addLayout(pwd_layout)
        
        # Check buttons
        btn_layout = QHBoxLayout()
        strength_btn = QPushButton("Check Strength")
        strength_btn.clicked.connect(self._check_password_strength)
        btn_layout.addWidget(strength_btn)
        
        common_btn = QPushButton("Check Common")
        common_btn.clicked.connect(self._check_common_password)
        btn_layout.addWidget(common_btn)
        layout.addLayout(btn_layout)
        
        # Results
        layout.addWidget(QLabel("Results:"))
        self.password_result = QTextEdit()
        self.password_result.setReadOnly(True)
        layout.addWidget(self.password_result)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_ssl_tab(self):
        """Create SSL/TLS check tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Target
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Host:"))
        self.ssl_host = QLineEdit()
        self.ssl_host.setPlaceholderText("e.g., example.com")
        host_layout.addWidget(self.ssl_host)
        layout.addLayout(host_layout)
        
        # Port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.ssl_port = QSpinBox()
        self.ssl_port.setValue(443)
        self.ssl_port.setMaximum(65535)
        port_layout.addWidget(self.ssl_port)
        layout.addLayout(port_layout)
        
        # Check button
        check_btn = QPushButton("Check Certificate")
        check_btn.clicked.connect(self._check_ssl)
        layout.addWidget(check_btn)
        
        # Results
        layout.addWidget(QLabel("Certificate Info:"))
        self.ssl_result = QTextEdit()
        self.ssl_result.setReadOnly(True)
        layout.addWidget(self.ssl_result)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_security_headers_tab(self):
        """Create security headers tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.headers_url = QLineEdit()
        self.headers_url.setPlaceholderText("e.g., https://example.com")
        url_layout.addWidget(self.headers_url)
        layout.addLayout(url_layout)
        
        # Check button
        check_btn = QPushButton("Check Headers")
        check_btn.clicked.connect(self._check_headers)
        layout.addWidget(check_btn)
        
        # Results
        layout.addWidget(QLabel("Headers:"))
        self.headers_table = QTableWidget()
        self.headers_table.setColumnCount(2)
        self.headers_table.setHorizontalHeaderLabels(["Header", "Value"])
        layout.addWidget(self.headers_table)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _scan_ports(self):
        """Scan ports"""
        host = self.scan_host.text()
        if not host:
            QMessageBox.warning(self, "Error", "Please enter target host")
            return
        
        try:
            results = self.tester.scan_ports(
                host,
                (self.port_start.value(), self.port_end.value())
            )
            
            open_ports = [p for p, is_open in results.items() if is_open]
            self.scan_results.setText(
                f"Scan Results for {host}:\n\n"
                f"Open Ports: {open_ports if open_ports else 'None'}\n\n"
                f"Total Scanned: {len(results)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _scan_common_ports(self):
        """Scan common ports"""
        host = self.scan_host.text()
        if not host:
            QMessageBox.warning(self, "Error", "Please enter target host")
            return
        
        try:
            results = self.tester.scan_common_ports(host)
            
            text = f"Common Port Scan Results for {host}:\n\n"
            for port, service in results.items():
                text += f"Port {port:5d} ({service:15s}): {'OPEN' if service != 'Closed' and service != 'Error' else service}\n"
            
            self.scan_results.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _generate_hash(self):
        """Generate hash"""
        text = self.hash_text.text()
        algo = self.hash_algo.currentText().lower()
        
        if not text:
            QMessageBox.warning(self, "Error", "Please enter text")
            return
        
        try:
            hash_value = self.tester.generate_hash(text, algo)
            self.hash_result.setText(f"{algo.upper()}:\n{hash_value}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _verify_hash(self):
        """Verify hash"""
        text = self.hash_text.text()
        hash_value = self.verify_hash.text()
        
        if not text or not hash_value:
            QMessageBox.warning(self, "Error", "Please enter text and hash")
            return
        
        try:
            results = self.tester.verify_hash(text, hash_value)
            
            text_result = "Verification Results:\n\n"
            for algo, is_match in results.items():
                text_result += f"{algo.upper()}: {'MATCH' if is_match else 'NO MATCH'}\n"
            
            self.verify_result.setText(text_result)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _check_password_strength(self):
        """Check password strength"""
        pwd = self.password_input.text()
        if not pwd:
            QMessageBox.warning(self, "Error", "Please enter password")
            return
        
        try:
            result = self.tester.check_password_strength(pwd)
            
            text = f"Password Strength: {result['strength']}\n"
            text += f"Score: {result['score']}/{result['max_score']}\n\n"
            
            if result['issues']:
                text += "Issues:\n"
                for issue in result['issues']:
                    text += f"- {issue}\n"
            else:
                text += "No issues found!"
            
            self.password_result.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _check_common_password(self):
        """Check if password is common"""
        pwd = self.password_input.text()
        if not pwd:
            QMessageBox.warning(self, "Error", "Please enter password")
            return
        
        try:
            is_common = self.tester.check_common_passwords(pwd)
            
            if is_common:
                self.password_result.setText("WARNING: This password is in the common passwords list!")
            else:
                self.password_result.setText("This password is NOT in the common passwords list.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _check_ssl(self):
        """Check SSL certificate"""
        host = self.ssl_host.text()
        if not host:
            QMessageBox.warning(self, "Error", "Please enter host")
            return
        
        try:
            result = self.tester.check_ssl_certificate(host, self.ssl_port.value())
            
            if result['valid']:
                text = "SSL Certificate Information:\n\n"
                for key, value in result.items():
                    if key != 'valid':
                        text += f"{key}: {value}\n"
            else:
                text = f"Error: {result.get('error', 'Unknown error')}"
            
            self.ssl_result.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _check_headers(self):
        """Check security headers"""
        url = self.headers_url.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter URL")
            return
        
        try:
            result = self.tester.check_security_headers(url)
            
            self.headers_table.setRowCount(len(result))
            row = 0
            for header, value in result.items():
                self.headers_table.setItem(row, 0, QTableWidgetItem(header))
                self.headers_table.setItem(row, 1, QTableWidgetItem(str(value) if value else "Not set"))
                row += 1
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
