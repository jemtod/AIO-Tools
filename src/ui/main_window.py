"""
Main Window Module
PyQt6 main application window
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QStatusBar, QMenuBar, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from .dumper_ui import DataDumperUI
from .security_ui import SecurityTesterUI
from .db_explorer_ui import DatabaseExplorerUI
from .dork_scanner_ui import DorkScannerUI


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("AIO TOOLS - by Jemtod")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Add tool tabs
        self.dumper_tab = DataDumperUI()
        tabs.addTab(self.dumper_tab, "Data Dumper")
        
        self.security_tab = SecurityTesterUI()
        tabs.addTab(self.security_tab, "Security Tester")
        
        self.db_tab = DatabaseExplorerUI()
        tabs.addTab(self.db_tab, "Database Explorer")
        
        self.dork_tab = DorkScannerUI()
        tabs.addTab(self.dork_tab, "Dork Scanner")
        
        # Set parent tabs reference for dork scanner
        self.dork_tab.parent_tabs = tabs
        
        layout.addWidget(tabs)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)
        
        help_action = help_menu.addAction("Documentation")
        help_action.triggered.connect(self._show_help)
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.information(
            self,
            "About DumpTools",
            "DumpTools v1.0\n\n"
            "A comprehensive Python-based GUI application for:\n"
            "- Data Dumping\n"
            "- Security Testing\n"
            "- Database Exploration\n\n"
            "For personal use and security testing.\n"
            "Use responsibly and only on systems you have permission to test."
        )
    
    def _show_help(self):
        """Show help dialog"""
        QMessageBox.information(
            self,
            "Help",
            "DumpTools Documentation\n\n"
            "1. Data Dumper Tab:\n"
            "   - Import data from JSON/CSV files\n"
            "   - Export to JSON, CSV, or SQL format\n"
            "   - Filter data by key-value pairs\n"
            "   - View dump history\n\n"
            "2. Security Tester Tab:\n"
            "   - Scan ports on target hosts\n"
            "   - Generate and verify hashes\n"
            "   - Check password strength\n"
            "   - Verify SSL/TLS certificates\n"
            "   - Check security headers\n\n"
            "3. Database Explorer Tab:\n"
            "   - Connect to SQLite databases\n"
            "   - Browse tables and schemas\n"
            "   - Preview table data\n"
            "   - Execute custom queries\n"
            "   - Export tables to various formats\n\n"
            "4. Dork Scanner Tab:\n"
            "   - Load and manage Google dork lists\n"
            "   - Detect SQL injection patterns in URLs\n"
            "   - Test common SQL injection payloads\n"
            "   - Check for SQL error messages\n"
            "   - Collect and export vulnerable URLs"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            'Exit',
            'Are you sure you want to exit?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
