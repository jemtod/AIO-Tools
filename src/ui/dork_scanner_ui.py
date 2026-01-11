"""
Dork Scanner UI Module
PyQt6 interface for Google dork scanning and SQL injection testing
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton,
    QLabel, QLineEdit, QComboBox, QTextEdit, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem, QSpinBox,
    QInputDialog, QProgressBar, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from tools import DorkScanner
from datetime import datetime
import threading


class ScanWorkerThread(QThread):
    """Worker thread for dork scanning"""
    progress_updated = pyqtSignal(int)
    scan_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, scanner, dorks, max_results):
        super().__init__()
        self.scanner = scanner
        self.dorks = dorks
        self.max_results = max_results
    
    def run(self):
        """Run scan in background thread"""
        try:
            results = self.scanner.scan_dorks_google(self.dorks, self.max_results)
            self.scan_complete.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))


class SingleDorkWorkerThread(QThread):
    """Worker thread for single dork scanning"""
    scan_complete = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, scanner, dork, max_results):
        super().__init__()
        self.scanner = scanner
        self.dork = dork
        self.max_results = max_results
    
    def run(self):
        """Run scan in background thread"""
        try:
            urls = self.scanner.scan_single_dork(self.dork, self.max_results)
            self.scan_complete.emit(urls)
        except Exception as e:
            self.error_occurred.emit(str(e))


class DorkScannerUI(QWidget):
    """Dork Scanner UI Component"""
    
    def __init__(self):
        super().__init__()
        self.scanner = DorkScanner()
        self.parent_tabs = None
        self.scan_thread = None
        self.single_dork_thread = None
        self._setup_logger_callbacks()
        self.init_ui()
    
    def _setup_logger_callbacks(self):
        """Setup logger callbacks"""
        def on_log(log_entry):
            # Update will happen in UI thread
            pass
        
        def on_progress(progress, current, total):
            # Update will happen in UI thread
            pass
        
        def on_complete():
            # Update will happen in UI thread
            pass
        
        self.scanner.logger.on_log = on_log
        self.scanner.logger.on_progress = on_progress
        self.scanner.logger.on_complete = on_complete
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Dork Scanner & SQL Injection Finder")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_dork_list_tab(), "Dork List")
        tabs.addTab(self._create_google_dorking_tab(), "Google Dorking")
        tabs.addTab(self._create_url_scanner_tab(), "URL Scanner")
        tabs.addTab(self._create_sql_injection_tab(), "SQL Injection")
        tabs.addTab(self._create_vulnerable_urls_tab(), "Vulnerable URLs")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    def _create_dork_list_tab(self):
        """Create dork list management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # File operations
        file_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load Dork File")
        load_btn.clicked.connect(self._load_dork_file)
        file_layout.addWidget(load_btn)
        
        default_btn = QPushButton("Load Default Dorks")
        default_btn.clicked.connect(self._load_default_dorks)
        file_layout.addWidget(default_btn)
        
        clear_btn = QPushButton("Clear List")
        clear_btn.clicked.connect(self._clear_dork_list)
        file_layout.addWidget(clear_btn)
        
        layout.addLayout(file_layout)
        
        # Add single dork
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("Add Dork:"))
        self.dork_input = QLineEdit()
        self.dork_input.setPlaceholderText("e.g., inurl:.php?id=")
        add_layout.addWidget(self.dork_input)
        
        add_dork_btn = QPushButton("Add")
        add_dork_btn.clicked.connect(self._add_single_dork)
        add_layout.addWidget(add_dork_btn)
        layout.addLayout(add_layout)
        
        # Dork list display
        layout.addWidget(QLabel("Current Dork List:"))
        self.dork_list_widget = QListWidget()
        layout.addWidget(self.dork_list_widget)
        
        # Statistics
        layout.addWidget(QLabel("Statistics:"))
        self.dork_stats = QTextEdit()
        self.dork_stats.setReadOnly(True)
        self.dork_stats.setMaximumHeight(150)
        layout.addWidget(self.dork_stats)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        analyze_btn = QPushButton("Analyze Dork List")
        analyze_btn.clicked.connect(self._analyze_dork_list)
        action_layout.addWidget(analyze_btn)
        
        # Start scanning button (prominent)
        start_btn = QPushButton("▶ START SCANNING URLs")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        start_btn.clicked.connect(self._switch_to_scan_tab)
        action_layout.addWidget(start_btn)
        
        layout.addLayout(action_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_google_dorking_tab(self):
        """Create Google dorking tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Scan options
        layout.addWidget(QLabel("Google Dorking - Collect URLs from Search Results"))
        layout.addWidget(QLabel("-" * 60))
        
        # Results limit
        results_layout = QHBoxLayout()
        results_layout.addWidget(QLabel("URLs per Dork:"))
        self.results_per_dork = QSpinBox()
        self.results_per_dork.setValue(5)
        self.results_per_dork.setMinimum(1)
        self.results_per_dork.setMaximum(50)
        results_layout.addWidget(self.results_per_dork)
        layout.addLayout(results_layout)
        
        # Main scanning buttons
        btn_layout = QHBoxLayout()
        
        # START SCANNING button (prominent)
        start_scan_btn = QPushButton("🔍 START SCANNING DORKS")
        start_scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 15px;
                font-size: 13px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        start_scan_btn.clicked.connect(self._start_dork_scanning)
        btn_layout.addWidget(start_scan_btn)
        
        # Single dork scan
        single_btn = QPushButton("Scan Single Dork")
        single_btn.clicked.connect(self._scan_single_dork)
        btn_layout.addWidget(single_btn)
        
        # Clear collected
        clear_btn = QPushButton("Clear Collected URLs")
        clear_btn.clicked.connect(self._clear_collected_urls)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        # Status
        self.dork_status = QLabel("Ready to scan. Load dorks first!")
        self.dork_status.setStyleSheet("color: #3498db; font-weight: bold;")
        layout.addWidget(self.dork_status)
        
        # Progress bar
        self.scan_progress = QProgressBar()
        self.scan_progress.setValue(0)
        layout.addWidget(self.scan_progress)
        
        # Logs display
        layout.addWidget(QLabel("Scan Progress Logs:"))
        self.scan_logs = QTextEdit()
        self.scan_logs.setReadOnly(True)
        self.scan_logs.setMaximumHeight(150)
        layout.addWidget(self.scan_logs)
        
        # Collected URLs
        layout.addWidget(QLabel("Collected URLs:"))
        self.collected_urls_widget = QListWidget()
        layout.addWidget(self.collected_urls_widget)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_txt_btn = QPushButton("Export URLs (TXT)")
        export_txt_btn.clicked.connect(lambda: self._export_collected_urls('txt'))
        export_layout.addWidget(export_txt_btn)
        
        export_csv_btn = QPushButton("Export URLs (CSV)")
        export_csv_btn.clicked.connect(lambda: self._export_collected_urls('csv'))
        export_layout.addWidget(export_csv_btn)
        
        layout.addLayout(export_layout)
        
        # Info
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(100)
        info_text.setText(
            "ℹ️ TIPS:\n"
            "• Load Default Dorks atau Custom Dorks dari 'Dork List' tab\n"
            "• Klik 'START SCANNING DORKS' untuk scan semua dorks\n"
            "• URLs akan dikumpulkan dari DuckDuckGo search results\n"
            "• Lihat progress logs di bagian 'Scan Progress Logs'\n"
            "• Berikutnya Anda bisa scan URLs untuk SQL Injection"
        )
        layout.addWidget(info_text)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_url_scanner_tab(self):
        """Create URL scanner tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Single URL test
        layout.addWidget(QLabel("Test URL for SQL Injection:"))
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.test_url = QLineEdit()
        self.test_url.setPlaceholderText("e.g., http://example.com/product.php?id=1")
        url_layout.addWidget(self.test_url)
        layout.addLayout(url_layout)
        
        # Test buttons
        btn_layout = QHBoxLayout()
        
        detect_btn = QPushButton("Detect Patterns")
        detect_btn.clicked.connect(self._detect_sql_patterns)
        btn_layout.addWidget(detect_btn)
        
        test_payload_btn = QPushButton("Test Payloads")
        test_payload_btn.clicked.connect(self._test_payloads)
        btn_layout.addWidget(test_payload_btn)
        
        check_errors_btn = QPushButton("Check SQL Errors")
        check_errors_btn.clicked.connect(self._check_sql_errors)
        btn_layout.addWidget(check_errors_btn)
        
        layout.addLayout(btn_layout)
        
        # Results
        layout.addWidget(QLabel("Analysis Results:"))
        self.scanner_results = QTextEdit()
        self.scanner_results.setReadOnly(True)
        layout.addWidget(self.scanner_results)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_sql_injection_tab(self):
        """Create SQL injection testing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Bulk URL testing
        layout.addWidget(QLabel("Bulk URL Testing:"))
        
        # URL list input
        layout.addWidget(QLabel("Enter URLs (one per line):"))
        self.bulk_urls = QTextEdit()
        self.bulk_urls.setPlaceholderText("http://example1.com/product.php?id=1\nhttp://example2.com/page.php?cat=1")
        layout.addWidget(self.bulk_urls)
        
        # Test options
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Risk Level:"))
        self.risk_filter = QComboBox()
        self.risk_filter.addItems(["All", "High", "Medium", "Low"])
        options_layout.addWidget(self.risk_filter)
        layout.addLayout(options_layout)
        
        # Scan button
        scan_btn = QPushButton("Scan URLs for Vulnerabilities")
        scan_btn.clicked.connect(self._scan_bulk_urls)
        layout.addWidget(scan_btn)
        
        # Results table
        layout.addWidget(QLabel("Scan Results:"))
        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(5)
        self.scan_table.setHorizontalHeaderLabels(["URL", "Risk Level", "Risk Score", "Issues", "Status"])
        layout.addWidget(self.scan_table)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_vulnerable_urls_tab(self):
        """Create vulnerable URLs management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Add new vulnerable URL
        add_layout = QVBoxLayout()
        add_layout.addWidget(QLabel("Add Vulnerable URL:"))
        
        url_input_layout = QHBoxLayout()
        url_input_layout.addWidget(QLabel("URL:"))
        self.vuln_url_input = QLineEdit()
        url_input_layout.addWidget(self.vuln_url_input)
        add_layout.addLayout(url_input_layout)
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.vuln_type = QComboBox()
        self.vuln_type.addItems(["SQL Injection", "XSS", "LFI", "RFI", "CSRF", "Other"])
        type_layout.addWidget(self.vuln_type)
        
        severity_layout = QHBoxLayout()
        severity_layout.addWidget(QLabel("Severity:"))
        self.vuln_severity = QComboBox()
        self.vuln_severity.addItems(["Critical", "High", "Medium", "Low"])
        severity_layout.addWidget(self.vuln_severity)
        
        type_layout.addLayout(severity_layout)
        add_layout.addLayout(type_layout)
        
        add_btn = QPushButton("Add URL")
        add_btn.clicked.connect(self._add_vulnerable_url)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # Vulnerable URLs list
        layout.addWidget(QLabel("Collected Vulnerable URLs:"))
        self.vuln_table = QTableWidget()
        self.vuln_table.setColumnCount(5)
        self.vuln_table.setHorizontalHeaderLabels(["URL", "Type", "Severity", "Risk Level", "Timestamp"])
        layout.addWidget(self.vuln_table)
        
        # Export options
        export_layout = QHBoxLayout()
        
        export_txt_btn = QPushButton("Export as TXT")
        export_txt_btn.clicked.connect(lambda: self._export_urls('txt'))
        export_layout.addWidget(export_txt_btn)
        
        export_csv_btn = QPushButton("Export as CSV")
        export_csv_btn.clicked.connect(lambda: self._export_urls('csv'))
        export_layout.addWidget(export_csv_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_vulnerable_urls)
        export_layout.addWidget(clear_btn)
        
        layout.addLayout(export_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    # ==================== Dork List Methods ====================
    def _load_dork_file(self):
        """Load dork file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Dork File", "", "Text Files (*.txt);;All Files (*.*)"
        )
        if filepath:
            success, count = self.scanner.load_dork_file(filepath)
            if success:
                self._refresh_dork_list()
                QMessageBox.information(self, "Success", f"Loaded {count} dorks")
            else:
                QMessageBox.critical(self, "Error", "Failed to load file")
    
    def _load_default_dorks(self):
        """Load default dorks"""
        default_dorks = self.scanner.get_default_dorks()
        self.scanner.clear_dork_list()
        
        for category, dorks in default_dorks.items():
            for dork in dorks:
                self.scanner.add_dork(dork)
        
        self._refresh_dork_list()
        QMessageBox.information(
            self, "Success",
            f"Loaded {sum(len(dorks) for dorks in default_dorks.values())} default dorks"
        )
    
    def _add_single_dork(self):
        """Add single dork"""
        dork = self.dork_input.text()
        if dork:
            self.scanner.add_dork(dork)
            self.dork_input.clear()
            self._refresh_dork_list()
        else:
            QMessageBox.warning(self, "Error", "Please enter a dork")
    
    def _clear_dork_list(self):
        """Clear dork list"""
        reply = QMessageBox.question(
            self, "Confirm", "Clear all dorks?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.scanner.clear_dork_list()
            self._refresh_dork_list()
    
    def _refresh_dork_list(self):
        """Refresh dork list display"""
        self.dork_list_widget.clear()
        for dork in self.scanner.get_dork_list():
            self.dork_list_widget.addItem(dork)
    
    def _analyze_dork_list(self):
        """Analyze dork list"""
        analysis = self.scanner.analyze_dork_list()
        
        text = f"Total Dorks: {analysis['total_dorks']}\n\n"
        text += "Breakdown:\n"
        for category, count in analysis['types'].items():
            text += f"  {category}: {count}\n"
        
        if analysis['sample_dorks']:
            text += "\nSample Dorks:\n"
            for dork in analysis['sample_dorks']:
                text += f"  - {dork}\n"
        
        self.dork_stats.setText(text)
    
    def _switch_to_scan_tab(self):
        """Switch to URL Scanner tab"""
        if self.scanner.get_dork_list():
            if self.parent_tabs:
                self.parent_tabs.setCurrentIndex(1)  # SQL Injection tab
            QMessageBox.information(
                self, "Ready",
                "Switched to SQL Injection Scanner.\n\n"
                "You can now:\n"
                "1. Enter URLs to scan\n"
                "2. Detect SQL injection patterns\n"
                "3. Test payloads\n"
                "4. Check for SQL errors"
            )
        else:
            QMessageBox.warning(
                self, "Error",
                "Please load a dork list first!"
            )
    
    # ==================== Google Dorking Methods ====================
    def _start_dork_scanning(self):
        """Start scanning all dorks"""
        dorks = self.scanner.get_dork_list()
        
        if not dorks:
            QMessageBox.warning(
                self, "Error",
                "No dorks to scan!\n\n"
                "Please:\n"
                "1. Go to 'Dork List' tab\n"
                "2. Click 'Load Default Dorks' or upload file\n"
                "3. Come back and click 'START SCANNING DORKS'"
            )
            return
        
        max_results = self.results_per_dork.value()
        
        reply = QMessageBox.question(
            self, "Confirm Scan",
            f"Scan {len(dorks)} dorks?\n"
            f"This will collect up to {len(dorks) * max_results} URLs\n\n"
            "Note: Using DuckDuckGo search engine\n"
            "This may take a few minutes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Clear previous logs and UI
        self.scanner.logger.clear_logs()
        self.scan_logs.clear()
        self.scan_progress.setValue(0)
        
        self.dork_status.setText("⏳ Scanning dorks... Please wait (this may take a few minutes)")
        self.dork_status.setStyleSheet("color: #f39c12; font-weight: bold;")
        
        # Start scan in background thread
        self.scan_thread = ScanWorkerThread(self.scanner, dorks, max_results)
        self.scan_thread.scan_complete.connect(self._on_scan_complete)
        self.scan_thread.error_occurred.connect(self._on_scan_error)
        self.scan_thread.start()
        
        # Update logs periodically
        self._update_logs_timer = QTimer()
        self._update_logs_timer.timeout.connect(self._update_logs_display)
        self._update_logs_timer.start(500)  # Update every 500ms
    
    def _on_scan_complete(self, results):
        """Handle scan completion"""
        # Stop log update timer
        if hasattr(self, '_update_logs_timer'):
            self._update_logs_timer.stop()
        
        # Final log update
        self._update_logs_display()
        
        if 'error' in results:
            self.dork_status.setText(f"⚠️ Error: {results['error']}")
            self.dork_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
            QMessageBox.critical(self, "Error", f"Scanning failed: {results['error']}")
            return
        
        # Update progress
        self.scan_progress.setValue(100)
        
        # Display collected URLs
        self._refresh_collected_urls()
        
        collected_count = len(self.scanner.get_collected_urls())
        self.dork_status.setText(f"✅ Scan complete! Collected {collected_count} URLs")
        self.dork_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        QMessageBox.information(
            self, "Scan Complete",
            f"Successfully scanned {len(self.scanner.get_dork_list())} dorks\n"
            f"Collected {collected_count} URLs\n\n"
            "You can now:\n"
            "1. Export URLs to file\n"
            "2. Go to 'SQL Injection' tab to scan URLs\n"
            "3. Add vulnerable URLs to collection"
        )
    
    def _on_scan_error(self, error_msg):
        """Handle scan error"""
        # Stop log update timer
        if hasattr(self, '_update_logs_timer'):
            self._update_logs_timer.stop()
        
        self.dork_status.setText(f"❌ Error: {error_msg}")
        self.dork_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self._update_logs_display()
        QMessageBox.critical(self, "Error", f"Scanning failed: {error_msg}")
    
    def _scan_single_dork(self):
        """Scan single dork"""
        dork, ok = QInputDialog.getText(
            self, "Scan Single Dork",
            "Enter dork to scan:",
            text="inurl:.php?id="
        )
        
        if not ok or not dork:
            return
        
        try:
            # Clear logs
            self.scanner.logger.clear_logs()
            self.scan_logs.clear()
            
            self.dork_status.setText(f"⏳ Scanning dork: {dork}")
            self.dork_status.setStyleSheet("color: #f39c12; font-weight: bold;")
            QApplication.processEvents()
            
            urls = self.scanner.scan_single_dork(dork, self.results_per_dork.value())
            
            # Update logs
            self._update_logs_display()
            
            if urls:
                self._refresh_collected_urls()
                self.dork_status.setText(f"✅ Found {len(urls)} URLs")
                self.dork_status.setStyleSheet("color: #27ae60; font-weight: bold;")
                QMessageBox.information(self, "Success", f"Found {len(urls)} URLs")
            else:
                self.dork_status.setText("❌ No URLs found")
                self.dork_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
                QMessageBox.warning(self, "No Results", "No URLs found for this dork")
        except Exception as e:
            self.dork_status.setText(f"❌ Error: {str(e)}")
            self._update_logs_display()
            QMessageBox.critical(self, "Error", str(e))
    
    def _update_logs_display(self):
        """Update logs display from logger"""
        logs = self.scanner.logger.get_logs()
        log_text = "\n".join([log['full_text'] for log in logs])
        self.scan_logs.setText(log_text)
        
        # Auto scroll to bottom
        scrollbar = self.scan_logs.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _refresh_collected_urls(self):
        """Refresh collected URLs display"""
        self.collected_urls_widget.clear()
        urls = self.scanner.get_collected_urls()
        
        for url in urls:
            item = QListWidgetItem(url)
            self.collected_urls_widget.addItem(item)
    
    def _clear_collected_urls(self):
        """Clear collected URLs"""
        reply = QMessageBox.question(
            self, "Confirm",
            "Clear all collected URLs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scanner.clear_collected_urls()
            self._refresh_collected_urls()
            self.dork_status.setText("✓ Cleared")
    
    def _export_collected_urls(self, format_type: str):
        """Export collected URLs"""
        urls = self.scanner.get_collected_urls()
        
        if not urls:
            QMessageBox.warning(self, "Error", "No URLs to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Collected URLs",
            f"collected_urls.{format_type}",
            f"{format_type.upper()} Files (*.{format_type});;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            if format_type == 'txt':
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Collected URLs from Google Dorking\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"Total: {len(urls)} URLs\n")
                    f.write(f"Date: {datetime.now().isoformat()}\n")
                    f.write("=" * 60 + "\n\n")
                    for url in urls:
                        f.write(f"{url}\n")
            
            elif format_type == 'csv':
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['URL', 'Collected Date'])
                    for url in urls:
                        writer.writerow([url, datetime.now().isoformat()])
            
            QMessageBox.information(self, "Success", f"Exported {len(urls)} URLs to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    # ==================== URL Scanner Methods ====================
    def _detect_sql_patterns(self):
        """Detect SQL injection patterns in URL"""
        url = self.test_url.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
        
        try:
            result = self.scanner.detect_sql_injection_patterns(url)
            
            text = f"URL Analysis:\n"
            text += f"{'='*50}\n\n"
            text += f"Risk Level: {result['risk_level']}\n"
            text += f"Risk Score: {result['risk_score']}/100\n\n"
            text += f"Issues Found:\n"
            
            if result['issues']:
                for issue in result['issues']:
                    text += f"  • {issue}\n"
            else:
                text += "  No issues found\n"
            
            self.scanner_results.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _test_payloads(self):
        """Test SQL injection payloads"""
        url = self.test_url.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
        
        try:
            result = self.scanner.test_sql_injection_payloads(url)
            
            text = f"Payload Testing Results:\n"
            text += f"{'='*50}\n\n"
            
            for i, payload_result in enumerate(result['tested_payloads'], 1):
                text += f"{i}. Payload: {payload_result['payload']}\n"
                if 'status_code' in payload_result:
                    text += f"   Status: {payload_result['status_code']}\n"
                    text += f"   Potentially Vulnerable: {'Yes' if payload_result['potentially_vulnerable'] else 'No'}\n"
                else:
                    text += f"   Error: {payload_result.get('error', 'Unknown')}\n"
                text += "\n"
            
            self.scanner_results.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _check_sql_errors(self):
        """Check for SQL error messages"""
        url = self.test_url.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
        
        try:
            result = self.scanner.check_sql_errors(url)
            
            text = f"SQL Error Detection:\n"
            text += f"{'='*50}\n\n"
            text += f"Response Code: {result.get('response_code', 'N/A')}\n"
            text += f"SQL Errors Found: {'Yes' if result['has_sql_errors'] else 'No'}\n\n"
            
            if result['has_sql_errors']:
                text += "Error Patterns Detected:\n"
                for pattern in result.get('error_patterns', []):
                    text += f"  • {pattern}\n"
            
            self.scanner_results.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    # ==================== Bulk Scan Methods ====================
    def _scan_bulk_urls(self):
        """Scan multiple URLs"""
        urls_text = self.bulk_urls.toPlainText()
        if not urls_text:
            QMessageBox.warning(self, "Error", "Please enter at least one URL")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        risk_filter = self.risk_filter.currentText()
        
        try:
            self.scan_table.setRowCount(len(urls))
            
            for row, url in enumerate(urls):
                result = self.scanner.detect_sql_injection_patterns(url)
                
                # Filter by risk level
                if risk_filter != "All" and result['risk_level'] != risk_filter:
                    continue
                
                self.scan_table.setItem(row, 0, QTableWidgetItem(url[:50]))
                self.scan_table.setItem(row, 1, QTableWidgetItem(result['risk_level']))
                self.scan_table.setItem(row, 2, QTableWidgetItem(str(result['risk_score'])))
                self.scan_table.setItem(row, 3, QTableWidgetItem(str(len(result['issues']))))
                self.scan_table.setItem(row, 4, QTableWidgetItem("Scanned"))
            
            QMessageBox.information(self, "Success", f"Scanned {len(urls)} URLs")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    # ==================== Vulnerable URLs Methods ====================
    def _add_vulnerable_url(self):
        """Add vulnerable URL"""
        url = self.vuln_url_input.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
        
        try:
            self.scanner.add_vulnerable_url(
                url,
                self.vuln_type.currentText(),
                self.vuln_severity.currentText()
            )
            self.vuln_url_input.clear()
            self._refresh_vulnerable_urls()
            QMessageBox.information(self, "Success", "URL added")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _refresh_vulnerable_urls(self):
        """Refresh vulnerable URLs table"""
        urls = self.scanner.get_vulnerable_urls()
        self.vuln_table.setRowCount(len(urls))
        
        for row, record in enumerate(urls):
            self.vuln_table.setItem(row, 0, QTableWidgetItem(record['url'][:50]))
            self.vuln_table.setItem(row, 1, QTableWidgetItem(record['type']))
            self.vuln_table.setItem(row, 2, QTableWidgetItem(record['severity']))
            self.vuln_table.setItem(row, 3, QTableWidgetItem(record['analysis']['risk_level']))
            self.vuln_table.setItem(row, 4, QTableWidgetItem(record['timestamp']))
    
    def _export_urls(self, format_type: str):
        """Export vulnerable URLs"""
        if not self.scanner.get_vulnerable_urls():
            QMessageBox.warning(self, "Error", "No vulnerable URLs to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Vulnerable URLs",
            f"vulnerable_urls.{format_type}",
            f"{format_type.upper()} Files (*.{format_type});;All Files (*.*)"
        )
        
        if file_path:
            if self.scanner.export_vulnerable_urls(file_path, format_type):
                QMessageBox.information(self, "Success", f"Exported to {file_path}")
            else:
                QMessageBox.critical(self, "Error", "Export failed")
    
    def _clear_vulnerable_urls(self):
        """Clear vulnerable URLs"""
        reply = QMessageBox.question(
            self, "Confirm", "Clear all vulnerable URLs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.scanner.clear_vulnerable_urls()
            self._refresh_vulnerable_urls()
            QMessageBox.information(self, "Success", "Cleared")
