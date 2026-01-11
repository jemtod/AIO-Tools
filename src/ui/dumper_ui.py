"""
Data Dumper UI Module
PyQt6 interface for data dumping tool
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton,
    QLabel, QLineEdit, QComboBox, QTextEdit, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QSpinBox
)
from PyQt6.QtCore import Qt
from tools import DataDumper


class DataDumperUI(QWidget):
    """Data Dumper UI Component"""
    
    def __init__(self):
        super().__init__()
        self.dumper = DataDumper()
        self.current_data = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Data Dumper Tool")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_import_tab(), "Import")
        tabs.addTab(self._create_export_tab(), "Export")
        tabs.addTab(self._create_filter_tab(), "Filter")
        tabs.addTab(self._create_history_tab(), "History")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_import_tab(self):
        """Create import tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.import_format = QComboBox()
        self.import_format.addItems(["JSON", "CSV"])
        format_layout.addWidget(self.import_format)
        layout.addLayout(format_layout)
        
        # File path
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File:"))
        self.import_path = QLineEdit()
        self.import_path.setPlaceholderText("Select file...")
        file_layout.addWidget(self.import_path)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_import_file)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)
        
        # Import button
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self._import_file)
        layout.addWidget(import_btn)
        
        # Preview
        layout.addWidget(QLabel("Preview:"))
        self.import_preview = QTextEdit()
        self.import_preview.setReadOnly(True)
        self.import_preview.setMaximumHeight(300)
        layout.addWidget(self.import_preview)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_export_tab(self):
        """Create export tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.export_format = QComboBox()
        self.export_format.addItems(["JSON", "CSV", "SQL"])
        format_layout.addWidget(self.export_format)
        layout.addLayout(format_layout)
        
        # Table name (for SQL)
        table_layout = QHBoxLayout()
        table_layout.addWidget(QLabel("Table Name:"))
        self.table_name = QLineEdit()
        self.table_name.setPlaceholderText("Table name for SQL export")
        table_layout.addWidget(self.table_name)
        layout.addLayout(table_layout)
        
        # Output path
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output:"))
        self.export_path = QLineEdit()
        self.export_path.setPlaceholderText("Select output path...")
        output_layout.addWidget(self.export_path)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_export_file)
        output_layout.addWidget(browse_btn)
        layout.addLayout(output_layout)
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self._export_file)
        layout.addWidget(export_btn)
        
        # Status
        self.export_status = QLabel("Ready")
        layout.addWidget(self.export_status)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_filter_tab(self):
        """Create filter tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Filter Data:"))
        
        # Filter key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key:"))
        self.filter_key = QLineEdit()
        key_layout.addWidget(self.filter_key)
        layout.addLayout(key_layout)
        
        # Filter value
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("Value:"))
        self.filter_value = QLineEdit()
        value_layout.addWidget(self.filter_value)
        layout.addLayout(value_layout)
        
        # Filter button
        filter_btn = QPushButton("Apply Filter")
        filter_btn.clicked.connect(self._apply_filter)
        layout.addWidget(filter_btn)
        
        # Results
        layout.addWidget(QLabel("Results:"))
        self.filter_results = QTextEdit()
        self.filter_results.setReadOnly(True)
        layout.addWidget(self.filter_results)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_history_tab(self):
        """Create history tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Dump History:"))
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(
            ["Timestamp", "Format", "Filename", "Records"]
        )
        layout.addWidget(self.history_table)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_history)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _browse_import_file(self):
        """Browse for import file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.import_path.setText(file_path)
    
    def _browse_export_file(self):
        """Browse for export file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "All Files (*.*)"
        )
        if file_path:
            self.export_path.setText(file_path)
    
    def _import_file(self):
        """Import file"""
        path = self.import_path.text()
        format_type = self.import_format.currentText()
        
        if not path:
            QMessageBox.warning(self, "Error", "Please select a file")
            return
        
        try:
            if format_type == "JSON":
                data = self.dumper.import_from_json(path)
            elif format_type == "CSV":
                data = self.dumper.import_from_csv(path)
            else:
                return
            
            if data:
                self.current_data = data
                self.import_preview.setText(str(data[:5]))  # Show first 5 records
                QMessageBox.information(self, "Success", f"Imported {len(data)} records")
            else:
                QMessageBox.warning(self, "Error", "Failed to import file")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _export_file(self):
        """Export file"""
        if not self.current_data:
            QMessageBox.warning(self, "Error", "No data to export")
            return
        
        path = self.export_path.text()
        format_type = self.export_format.currentText()
        
        if not path:
            QMessageBox.warning(self, "Error", "Please select output path")
            return
        
        try:
            if format_type == "JSON":
                success = self.dumper.export_to_json(self.current_data, path)
            elif format_type == "CSV":
                success = self.dumper.export_to_csv(self.current_data, path)
            elif format_type == "SQL":
                table = self.table_name.text() or "data"
                success = self.dumper.export_to_sql(self.current_data, table, path)
            else:
                return
            
            if success:
                self.export_status.setText(f"Exported to {path}")
                QMessageBox.information(self, "Success", "Export completed")
            else:
                QMessageBox.warning(self, "Error", "Export failed")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _apply_filter(self):
        """Apply filter to data"""
        if not self.current_data:
            QMessageBox.warning(self, "Error", "No data loaded")
            return
        
        key = self.filter_key.text()
        value = self.filter_value.text()
        
        if not key:
            QMessageBox.warning(self, "Error", "Please enter filter key")
            return
        
        try:
            filtered = self.dumper.filter_data(
                self.current_data,
                {key: value}
            )
            self.filter_results.setText(
                f"Found {len(filtered)} records\n\n{str(filtered)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _refresh_history(self):
        """Refresh history table"""
        history = self.dumper.get_dump_history()
        self.history_table.setRowCount(len(history))
        
        for row, record in enumerate(history):
            self.history_table.setItem(row, 0, QTableWidgetItem(record['timestamp']))
            self.history_table.setItem(row, 1, QTableWidgetItem(record['format']))
            self.history_table.setItem(row, 2, QTableWidgetItem(record['filename']))
            self.history_table.setItem(row, 3, QTableWidgetItem(str(record['records'])))
