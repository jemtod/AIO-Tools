"""
Dork Scanner UI Module
PyQt6 interface for Google dork scanning and SQL injection testing
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton,
    QLabel, QLineEdit, QComboBox, QTextEdit, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem, QSpinBox,
    QInputDialog, QProgressBar, QApplication, QMenu
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


class SQLiScannerThread(QThread):
    """Worker thread for SQL injection scanning"""
    url_scanned = pyqtSignal(dict)  # Emits result dict
    scan_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(int, int)  # current, total
    
    def __init__(self, scanner, urls):
        super().__init__()
        self.scanner = scanner
        self.urls = urls
        self.running = True
    
    def run(self):
        """Run SQL injection scanning in background thread"""
        try:
            for idx, url in enumerate(self.urls):
                if not self.running:
                    break
                
                try:
                    # Perform all checks
                    pattern_result = self.scanner.detect_sql_injection_patterns(url)
                    payload_result = self.scanner.test_sql_injection_payloads(url)
                    error_result = self.scanner.check_sql_errors(url)
                    
                    # Emit result
                    result = {
                        'url': url,
                        'pattern_result': pattern_result,
                        'payload_result': payload_result,
                        'error_result': error_result
                    }
                    self.url_scanned.emit(result)
                    self.progress_update.emit(idx + 1, len(self.urls))
                    
                except Exception as e:
                    self.error_occurred.emit(f"Error scanning {url}: {str(e)}")
            
            self.scan_complete.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """Stop scanning"""
        self.running = False


class DorkScannerUI(QWidget):
    """Dork Scanner UI Component"""
    
    def __init__(self):
        super().__init__()
        self.scanner = DorkScanner()
        self.parent_tabs = None
        self.scan_thread = None
        self.single_dork_thread = None
        self.sqli_scan_thread = None
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
        self.main_tabs = QTabWidget()
        self.main_tabs.addTab(self._create_dork_list_tab(), "Dork List")
        self.main_tabs.addTab(self._create_google_dorking_tab(), "Google Dorking")
        self.main_tabs.addTab(self._create_url_scanner_tab(), "URL Scanner")
        self.sql_injection_tab = self._create_sql_injection_tab()
        self.main_tabs.addTab(self.sql_injection_tab, "SQL Injection")
        self.main_tabs.addTab(self._create_database_dumper_tab(), "Dump SQL")
        self.main_tabs.addTab(self._create_vulnerable_urls_tab(), "Vulnerable URLs")
        
        layout.addWidget(self.main_tabs)
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
        
        # Proxy settings
        proxy_layout = QHBoxLayout()
        proxy_layout.addWidget(QLabel("HTTP Proxy:"))
        self.http_proxy_input = QLineEdit()
        self.http_proxy_input.setPlaceholderText("host:port or host:port:user:pass")
        proxy_layout.addWidget(self.http_proxy_input)
        proxy_layout.addWidget(QLabel("HTTPS Proxy:"))
        self.https_proxy_input = QLineEdit()
        self.https_proxy_input.setPlaceholderText("host:port or host:port:user:pass")
        proxy_layout.addWidget(self.https_proxy_input)
        apply_proxy_btn = QPushButton("Apply Proxy")
        apply_proxy_btn.clicked.connect(self._apply_proxy_settings)
        proxy_layout.addWidget(apply_proxy_btn)
        layout.addLayout(proxy_layout)
        
        self.proxy_status = QLabel("Proxy: direct connection")
        self.proxy_status.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.proxy_status)
        
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
        """Create SQL injection testing tab - SQLi Dumper style"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # URL Queue section
        layout.addWidget(QLabel("URL Queue - Automatic SQL Injection Scanner:"))
        
        # URL input
        url_input_layout = QHBoxLayout()
        url_input_layout.addWidget(QLabel("URLs (one per line):"))
        self.bulk_urls = QTextEdit()
        self.bulk_urls.setPlaceholderText("http://example1.com/product.php?id=1\nhttp://example2.com/page.php?cat=1")
        self.bulk_urls.setMaximumHeight(120)
        url_input_layout.addWidget(self.bulk_urls)
        layout.addLayout(url_input_layout)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_scan_btn = QPushButton("▶ Start Scanner")
        self.start_scan_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        self.start_scan_btn.clicked.connect(self._start_sqli_scanner)
        control_layout.addWidget(self.start_scan_btn)
        
        self.stop_scan_btn = QPushButton("⏸ Stop Scanner")
        self.stop_scan_btn.setEnabled(False)
        self.stop_scan_btn.clicked.connect(self._stop_sqli_scanner)
        control_layout.addWidget(self.stop_scan_btn)
        
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self._clear_sqli_results)
        control_layout.addWidget(clear_btn)
        
        layout.addLayout(control_layout)
        
        # Statistics
        stats_layout = QHBoxLayout()
        self.scan_stats = QLabel("Queue: 0 | Exploitables: 0 | Injectables: 0 | Non-Injectables: 0")
        self.scan_stats.setStyleSheet("font-weight: bold; color: #3498db;")
        stats_layout.addWidget(self.scan_stats)
        layout.addLayout(stats_layout)
        
        # Category tabs for results
        self.result_tabs = QTabWidget()
        
        # Exploitables tab
        self.exploitable_table = self._create_result_table()
        self.result_tabs.addTab(self.exploitable_table, "Exploitables (0)")
        
        # Injectables tab
        self.injectable_table = self._create_result_table()
        self.result_tabs.addTab(self.injectable_table, "Injectables (0)")
        
        # Non-Injectables tab
        self.non_injectable_table = self._create_result_table()
        self.result_tabs.addTab(self.non_injectable_table, "Non-Injectables (0)")
        
        layout.addWidget(self.result_tabs)
        
        # Action buttons for selected URLs
        action_layout = QHBoxLayout()
        self.dump_btn = QPushButton("🗂️ Go to Dumper")
        self.dump_btn.clicked.connect(self._go_to_dumper)
        action_layout.addWidget(self.dump_btn)
        
        export_exploitable_btn = QPushButton("Export Exploitables")
        export_exploitable_btn.clicked.connect(lambda: self._export_results('exploitable'))
        action_layout.addWidget(export_exploitable_btn)
        
        layout.addLayout(action_layout)
        
        # Initialize counters
        self.exploitable_count = 0
        self.injectable_count = 0
        self.non_injectable_count = 0
        
        widget.setLayout(layout)
        return widget
    
    def _create_result_table(self):
        """Create a result table for SQL injection results"""
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "URL", "Method", "SQL Type", "Risk Level", 
            "Parameters", "Server", "Country", "Status"
        ])
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self._show_result_context_menu)
        return table
    
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
    def _apply_proxy_settings(self):
        """Apply proxy settings to scanner"""
        proxies = self.scanner.set_proxies(
            self.http_proxy_input.text(),
            self.https_proxy_input.text()
        )
        if proxies:
            http_desc = proxies.get('http', '—')
            https_desc = proxies.get('https', '—')
            self.proxy_status.setText(f"Proxy enabled (http: {http_desc}, https: {https_desc})")
            self.proxy_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.proxy_status.setText("Proxy: direct connection")
            self.proxy_status.setStyleSheet("color: #7f8c8d;")
    
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
        
        # Apply latest proxies before starting
        self._apply_proxy_settings()
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
        
        # Auto-populate SQL Injection tab and navigate
        if collected_count > 0:
            reply = QMessageBox.question(
                self, "Scan Complete",
                f"Successfully scanned {len(self.scanner.get_dork_list())} dorks\n"
                f"Collected {collected_count} URLs\n\n"
                "Auto-navigate to SQL Injection tab and populate URLs for scanning?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Populate bulk URLs in SQL Injection tab
                self._auto_populate_sql_injection_urls()
                # Switch to SQL Injection tab
                self.main_tabs.setCurrentIndex(3)  # Index 3 = SQL Injection tab
                
                # Show confirmation
                QMessageBox.information(
                    self, "Ready",
                    f"URLs populated in SQL Injection tab.\n\n"
                    f"Click 'Scan URLs for Vulnerabilities' to start scanning\n"
                    f"or customize the list before scanning."
                )
            else:
                QMessageBox.information(
                    self, "Scan Complete",
                    f"You can export URLs or manually navigate to SQL Injection tab later."
                )
        else:
            QMessageBox.information(
                self, "Scan Complete",
                "No URLs collected. Try different dorks or adjust settings."
            )
    
    def _auto_populate_sql_injection_urls(self):
        """Auto-populate SQL Injection tab with collected URLs"""
        urls = self.scanner.get_collected_urls()
        if urls:
            url_text = "\n".join(urls)
            self.bulk_urls.setText(url_text)
    
    
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
            # Apply latest proxies and clear logs
            self._apply_proxy_settings()
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
            self._apply_proxy_settings()
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
            self._apply_proxy_settings()
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
    def _start_sqli_scanner(self):
        """Start SQL injection scanner - SQLi Dumper style (background thread)"""
        urls_text = self.bulk_urls.toPlainText()
        if not urls_text:
            QMessageBox.warning(self, "Error", "Please enter at least one URL in the queue")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        reply = QMessageBox.question(
            self, "Start Scanner",
            f"Start scanning {len(urls)} URLs?\n\n"
            "The scanner will automatically test for SQL injection vulnerabilities.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Reset counters
        self.exploitable_count = 0
        self.injectable_count = 0
        self.non_injectable_count = 0
        
        # Clear tables
        self.exploitable_table.setRowCount(0)
        self.injectable_table.setRowCount(0)
        self.non_injectable_table.setRowCount(0)
        
        # Update UI
        self.start_scan_btn.setEnabled(False)
        self.stop_scan_btn.setEnabled(True)
        
        # Apply proxy if configured
        self._apply_proxy_settings()
        
        # Start background thread for scanning
        self.sqli_scan_thread = SQLiScannerThread(self.scanner, urls)
        self.sqli_scan_thread.url_scanned.connect(self._on_url_scanned)
        self.sqli_scan_thread.progress_update.connect(self._on_scan_progress)
        self.sqli_scan_thread.scan_complete.connect(self._on_sqli_scan_complete)
        self.sqli_scan_thread.error_occurred.connect(self._on_sqli_scan_error)
        self.sqli_scan_thread.start()
    
    def _on_url_scanned(self, result):
        """Handle individual URL scan result"""
        url = result['url']
        pattern_result = result['pattern_result']
        error_result = result['error_result']
        
        risk_level = pattern_result['risk_level']
        has_sql_errors = error_result.get('has_sql_errors', False)
        
        # Extract info from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        params = parsed.query.split('&') if parsed.query else []
        
        # Determine category
        if risk_level == "High" and has_sql_errors:
            category = "exploitable"
            self.exploitable_count += 1
        elif risk_level in ["Medium", "High"]:
            category = "injectable"
            self.injectable_count += 1
        else:
            category = "non-injectable"
            self.non_injectable_count += 1
        
        # Add to appropriate table
        self._add_result_to_table(category, {
            'url': url,
            'method': 'GET',
            'sql_type': 'MySQL' if has_sql_errors else 'Unknown',
            'risk_level': risk_level,
            'parameters': str(len(params)),
            'server': error_result.get('response_code', 'Unknown'),
            'country': 'Unknown',
            'status': 'Tested'
        })
        
        # Update statistics
        self._update_scan_statistics()
    
    def _on_scan_progress(self, current, total):
        """Update progress during scanning"""
        pass  # UI will auto-update from result counts
    
    def _on_sqli_scan_complete(self):
        """Handle SQL injection scan completion"""
        self.start_scan_btn.setEnabled(True)
        self.stop_scan_btn.setEnabled(False)
        
        QMessageBox.information(
            self, "Scan Complete",
            f"Scanning finished!\n\n"
            f"Exploitables: {self.exploitable_count}\n"
            f"Injectables: {self.injectable_count}\n"
            f"Non-Injectables: {self.non_injectable_count}"
        )
    
    def _on_sqli_scan_error(self, error_msg):
        """Handle SQL injection scan error"""
        self.start_scan_btn.setEnabled(True)
        self.stop_scan_btn.setEnabled(False)
        QMessageBox.critical(self, "Error", f"Scanning error: {error_msg}")
    
    def _stop_sqli_scanner(self):
        """Stop SQL injection scanner"""
        if self.sqli_scan_thread:
            self.sqli_scan_thread.stop()
            self.sqli_scan_thread.wait()
        
        self.start_scan_btn.setEnabled(True)
        self.stop_scan_btn.setEnabled(False)
    
    def _add_result_to_table(self, category, data):
        """Add result to appropriate category table"""
        if category == "exploitable":
            table = self.exploitable_table
        elif category == "injectable":
            table = self.injectable_table
        else:
            table = self.non_injectable_table
        
        row = table.rowCount()
        table.insertRow(row)
        
        table.setItem(row, 0, QTableWidgetItem(data['url'][:60]))
        table.setItem(row, 1, QTableWidgetItem(data['method']))
        table.setItem(row, 2, QTableWidgetItem(data['sql_type']))
        table.setItem(row, 3, QTableWidgetItem(data['risk_level']))
        table.setItem(row, 4, QTableWidgetItem(data['parameters']))
        table.setItem(row, 5, QTableWidgetItem(str(data['server'])))
        table.setItem(row, 6, QTableWidgetItem(data['country']))
        table.setItem(row, 7, QTableWidgetItem(data['status']))
    
    def _update_scan_statistics(self):
        """Update scan statistics display"""
        total = self.exploitable_count + self.injectable_count + self.non_injectable_count
        self.scan_stats.setText(
            f"Queue: {total} | Exploitables: {self.exploitable_count} | "
            f"Injectables: {self.injectable_count} | Non-Injectables: {self.non_injectable_count}"
        )
        
        # Update tab titles
        self.result_tabs.setTabText(0, f"Exploitables ({self.exploitable_count})")
        self.result_tabs.setTabText(1, f"Injectables ({self.injectable_count})")
        self.result_tabs.setTabText(2, f"Non-Injectables ({self.non_injectable_count})")
    
    def _clear_sqli_results(self):
        """Clear all SQL injection scan results"""
        self.exploitable_table.setRowCount(0)
        self.injectable_table.setRowCount(0)
        self.non_injectable_table.setRowCount(0)
        
        self.exploitable_count = 0
        self.injectable_count = 0
        self.non_injectable_count = 0
        
        self._update_scan_statistics()
    
    def _show_result_context_menu(self, position):
        """Show context menu for result table"""
        menu = QMenu()
        
        copy_url_action = menu.addAction("Copy URL")
        go_to_dumper_action = menu.addAction("Go to Dumper")
        reanalyze_action = menu.addAction("Re-Analyze")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(self.sender().mapToGlobal(position))
        
        if action == copy_url_action:
            self._copy_selected_url()
        elif action == go_to_dumper_action:
            self._go_to_dumper()
        elif action == reanalyze_action:
            self._reanalyze_selected()
        elif action == delete_action:
            self._delete_selected_result()
    
    def _copy_selected_url(self):
        """Copy selected URL to clipboard"""
        current_table = self.result_tabs.currentWidget()
        if isinstance(current_table, QTableWidget):
            selected = current_table.selectedItems()
            if selected:
                url = current_table.item(selected[0].row(), 0).text()
                QApplication.clipboard().setText(url)
    
    def _go_to_dumper(self):
        """Navigate to Database Explorer with selected URL"""
        current_table = self.result_tabs.currentWidget()
        if isinstance(current_table, QTableWidget):
            selected = current_table.selectedItems()
            if selected:
                url = current_table.item(selected[0].row(), 0).text()
                QMessageBox.information(
                    self, "Go to Dumper",
                    f"Database dumping feature will be available soon.\n\n"
                    f"Selected URL: {url}\n\n"
                    "This will allow you to:\n"
                    "• Extract database names\n"
                    "• Dump table structures\n"
                    "• Extract data from tables"
                )
    
    def _reanalyze_selected(self):
        """Re-analyze selected URL"""
        current_table = self.result_tabs.currentWidget()
        if isinstance(current_table, QTableWidget):
            selected = current_table.selectedItems()
            if selected:
                url = current_table.item(selected[0].row(), 0).text()
                # Create single URL list and scan
                self.bulk_urls.setText(url)
                self._start_sqli_scanner()
    
    def _delete_selected_result(self):
        """Delete selected result from table"""
        current_table = self.result_tabs.currentWidget()
        if isinstance(current_table, QTableWidget):
            selected = current_table.selectedItems()
            if selected:
                current_table.removeRow(selected[0].row())
                # Update counters based on which table
                if current_table == self.exploitable_table:
                    self.exploitable_count = max(0, self.exploitable_count - 1)
                elif current_table == self.injectable_table:
                    self.injectable_count = max(0, self.injectable_count - 1)
                else:
                    self.non_injectable_count = max(0, self.non_injectable_count - 1)
                self._update_scan_statistics()
    
    def _export_results(self, category):
        """Export results from specific category"""
        if category == 'exploitable':
            table = self.exploitable_table
            title = "Exploitable URLs"
        elif category == 'injectable':
            table = self.injectable_table
            title = "Injectable URLs"
        else:
            table = self.non_injectable_table
            title = "Non-Injectable URLs"
        
        if table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", f"No {category} URLs to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export {title}",
            f"{category}_urls.txt",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"{title}\n")
                f.write("=" * 60 + "\n\n")
                
                for row in range(table.rowCount()):
                    url = table.item(row, 0).text()
                    method = table.item(row, 1).text()
                    sql_type = table.item(row, 2).text()
                    risk = table.item(row, 3).text()
                    
                    f.write(f"URL: {url}\n")
                    f.write(f"Method: {method}, SQL Type: {sql_type}, Risk: {risk}\n")
                    f.write("-" * 60 + "\n")
            
            QMessageBox.information(self, "Success", f"Exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _scan_bulk_urls(self):
        """Legacy method - redirect to new scanner"""
        self._start_sqli_scanner()

    
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
    
    def _create_database_dumper_tab(self):
        """Create database dumper tab"""
        from tools import SQLDumper
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Target URL:"))
        self.dump_url_input = QLineEdit()
        self.dump_url_input.setPlaceholderText("http://example.com/page.php?id=1")
        url_layout.addWidget(self.dump_url_input)
        layout.addLayout(url_layout)
        
        # Keywords to search
        keyword_layout = QHBoxLayout()
        keyword_layout.addWidget(QLabel("Keywords (comma-separated):"))
        self.dump_keywords_input = QLineEdit()
        self.dump_keywords_input.setText("user,pass,email,password,username,admin,login")
        self.dump_keywords_input.setPlaceholderText("user,pass,email,password")
        keyword_layout.addWidget(self.dump_keywords_input)
        layout.addLayout(keyword_layout)
        
        # Database Info & Schema
        info_layout = QHBoxLayout()
        get_info_btn = QPushButton("Get DB Info & Schema")
        get_info_btn.clicked.connect(self._get_database_info)
        info_layout.addWidget(get_info_btn)
        
        dump_btn = QPushButton("Dump by Keywords")
        dump_btn.clicked.connect(self._start_database_dump)
        dump_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        info_layout.addWidget(dump_btn)
        
        export_btn = QPushButton("Export Results")
        export_btn.clicked.connect(self._export_dump_results)
        info_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self._clear_dump_results)
        info_layout.addWidget(clear_btn)
        
        layout.addLayout(info_layout)
        
        # Results display - Tab widget for different result types
        self.dump_tabs = QTabWidget()
        
        # Database Info tab
        self.db_info_text = QTextEdit()
        self.db_info_text.setReadOnly(True)
        self.dump_tabs.addTab(self.db_info_text, "Database Info")
        
        # Schema tab
        self.db_schema_text = QTextEdit()
        self.db_schema_text.setReadOnly(True)
        self.dump_tabs.addTab(self.db_schema_text, "Schema")
        
        # Dumped Data tab
        self.dump_results_table = QTableWidget()
        self.dump_results_table.setColumnCount(3)
        self.dump_results_table.setHorizontalHeaderLabels(["Column", "Records", "Data"])
        self.dump_results_table.resizeColumnToContents(0)
        self.dump_tabs.addTab(self.dump_results_table, "Dumped Data")
        
        # Raw Log tab
        self.dump_log_text = QTextEdit()
        self.dump_log_text.setReadOnly(True)
        self.dump_tabs.addTab(self.dump_log_text, "Log")
        
        layout.addWidget(self.dump_tabs)
        
        # Progress label
        self.dump_status_label = QLabel("Ready")
        layout.addWidget(self.dump_status_label)
        
        widget.setLayout(layout)
        self.dumper = SQLDumper()
        self.dump_results = {}
        
        return widget
    
    def _get_database_info(self):
        """Get database information and schema"""
        url = self.dump_url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a target URL")
            return
        
        self.dump_status_label.setText("Fetching database info...")
        QApplication.processEvents()
        
        try:
            # Get database info
            info = self.dumper.get_database_info(url)
            
            info_text = "DATABASE INFORMATION\n"
            info_text += "=" * 60 + "\n\n"
            
            if info:
                for key, value in info.items():
                    info_text += f"{key.upper()}: {value or 'Unknown'}\n"
            else:
                info_text += "Could not retrieve database information.\n"
                info_text += "Target may not be vulnerable to SQL injection.\n"
            
            self.db_info_text.setText(info_text)
            
            # Get schema
            schema = self.dumper.extract_database_schema(url)
            
            schema_text = "DATABASE SCHEMA\n"
            schema_text += "=" * 60 + "\n\n"
            
            if schema:
                for table, columns in schema.items():
                    schema_text += f"TABLE: {table}\n"
                    schema_text += f"  Columns: {', '.join(columns)}\n\n"
            else:
                schema_text += "Could not retrieve database schema.\n"
            
            self.db_schema_text.setText(schema_text)
            self.dump_status_label.setText("Database info retrieved successfully")
            
        except Exception as e:
            self.dump_status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to retrieve database info:\n{str(e)}")
    
    def _start_database_dump(self):
        """Start database dumping process"""
        url = self.dump_url_input.text().strip()
        keywords_str = self.dump_keywords_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a target URL")
            return
        
        if not keywords_str:
            QMessageBox.warning(self, "Error", "Please enter keywords to search for")
            return
        
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
        
        self.dump_status_label.setText(f"Dumping database for keywords: {', '.join(keywords)}...")
        self.dump_results_table.setRowCount(0)
        QApplication.processEvents()
        
        try:
            # Start dumping
            self.dump_results = self.dumper.dump_database_by_keyword(url, keywords, limit=50)
            
            if not self.dump_results:
                self.dump_status_label.setText("No matching columns found or dump failed")
                return
            
            # Display results
            self.dump_results_table.setRowCount(len(self.dump_results))
            
            for row, (column_name, data) in enumerate(self.dump_results.items()):
                self.dump_results_table.setItem(row, 0, QTableWidgetItem(column_name))
                self.dump_results_table.setItem(row, 1, QTableWidgetItem(str(len(data))))
                
                # Show first 5 values
                preview = " | ".join(data[:5])
                if len(data) > 5:
                    preview += f" ... (+{len(data)-5} more)"
                
                item = QTableWidgetItem(preview)
                item.setToolTip("\n".join(data[:20]))  # Tooltip shows more values
                self.dump_results_table.setItem(row, 2, item)
            
            self.dump_results_table.resizeColumnsToContents()
            self.dump_status_label.setText(f"Successfully dumped {len(self.dump_results)} columns")
            
        except Exception as e:
            self.dump_status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Dump failed:\n{str(e)}")
    
    def _export_dump_results(self):
        """Export dumped data to file"""
        if not self.dump_results:
            QMessageBox.warning(self, "Error", "No dumped data to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Dumped Data",
            "database_dump.txt",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*.*)"
        )
        
        if file_path:
            format_type = 'csv' if file_path.endswith('.csv') else 'txt'
            if self.dumper.export_dump_to_file(self.dump_results, file_path, format_type):
                QMessageBox.information(self, "Success", f"Dumped data exported to:\n{file_path}")
            else:
                QMessageBox.critical(self, "Error", "Export failed")
    
    def _clear_dump_results(self):
        """Clear dump results"""
        self.dump_results = {}
        self.dump_results_table.setRowCount(0)
        self.db_info_text.clear()
        self.db_schema_text.clear()
        self.dump_log_text.clear()
        self.dump_status_label.setText("Ready")

