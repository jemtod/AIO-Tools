"""
Database Explorer UI Module
PyQt6 interface for database exploration
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QTextEdit, QFileDialog,
    QMessageBox, QTableWidget, QTableWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt
from tools import DatabaseExplorer


class DatabaseExplorerUI(QWidget):
    """Database Explorer UI Component"""
    
    def __init__(self):
        super().__init__()
        self.explorer = DatabaseExplorer()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Database Explorer")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Connection controls
        conn_layout = QHBoxLayout()
        conn_layout.addWidget(QLabel("Database:"))
        self.db_path = QLineEdit()
        self.db_path.setPlaceholderText("SQLite database path")
        conn_layout.addWidget(self.db_path)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_database)
        conn_layout.addWidget(browse_btn)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self._connect_database)
        conn_layout.addWidget(connect_btn)
        
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.clicked.connect(self._disconnect_database)
        conn_layout.addWidget(disconnect_btn)
        
        layout.addLayout(conn_layout)
        
        # Main content - Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Tables list
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Tables:"))
        
        self.tables_list = QListWidget()
        self.tables_list.itemClicked.connect(self._on_table_selected)
        left_layout.addWidget(self.tables_list)
        
        refresh_btn = QPushButton("Refresh Tables")
        refresh_btn.clicked.connect(self._refresh_tables)
        left_layout.addWidget(refresh_btn)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        # Right panel - Table details
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Table info
        right_layout.addWidget(QLabel("Table Information:"))
        self.table_info = QTextEdit()
        self.table_info.setReadOnly(True)
        self.table_info.setMaximumHeight(150)
        right_layout.addWidget(self.table_info)
        
        # Table data
        right_layout.addWidget(QLabel("Data Preview:"))
        self.data_table = QTableWidget()
        right_layout.addWidget(self.data_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        export_btn = QPushButton("Export Table")
        export_btn.clicked.connect(self._export_table)
        action_layout.addWidget(export_btn)
        
        query_btn = QPushButton("Custom Query")
        query_btn.clicked.connect(self._open_query_dialog)
        action_layout.addWidget(query_btn)
        right_layout.addLayout(action_layout)
        
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        self._refresh_connection_status()
    
    def _browse_database(self):
        """Browse for database file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Database", "", "SQLite (*.db *.sqlite *.sqlite3);;All Files (*.*)"
        )
        if file_path:
            self.db_path.setText(file_path)
    
    def _connect_database(self):
        """Connect to database"""
        path = self.db_path.text()
        if not path:
            QMessageBox.warning(self, "Error", "Please select a database")
            return
        
        try:
            if self.explorer.create_sqlite_connection(path):
                QMessageBox.information(self, "Success", "Connected to database")
                self._refresh_tables()
                self._refresh_connection_status()
            else:
                QMessageBox.critical(self, "Error", "Failed to connect")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _disconnect_database(self):
        """Disconnect from database"""
        if self.explorer.disconnect():
            self.tables_list.clear()
            self.data_table.setRowCount(0)
            self.table_info.clear()
            QMessageBox.information(self, "Success", "Disconnected")
            self._refresh_connection_status()
    
    def _refresh_tables(self):
        """Refresh tables list"""
        tables = self.explorer.get_tables()
        self.tables_list.clear()
        
        for table in tables:
            self.tables_list.addItem(table)
    
    def _on_table_selected(self, item):
        """Handle table selection"""
        table_name = item.text()
        self._show_table_info(table_name)
        self._show_table_preview(table_name)
    
    def _show_table_info(self, table_name: str):
        """Show table information"""
        try:
            info = self.explorer.get_table_info(table_name)
            
            text = f"Table: {info['name']}\n"
            text += f"Rows: {info['row_count']}\n\n"
            
            if 'schema' in info and 'columns' in info['schema']:
                text += "Columns:\n"
                for col in info['schema']['columns']:
                    text += f"  - {col['name']} ({col['type']})"
                    if col['primary_key']:
                        text += " [PRIMARY KEY]"
                    if col['not_null']:
                        text += " [NOT NULL]"
                    text += "\n"
            
            self.table_info.setText(text)
        except Exception as e:
            self.table_info.setText(f"Error: {str(e)}")
    
    def _show_table_preview(self, table_name: str):
        """Show table preview"""
        try:
            data = self.explorer.get_table_preview(table_name)
            
            if not data:
                self.data_table.setRowCount(0)
                return
            
            # Set columns
            columns = list(data[0].keys())
            self.data_table.setColumnCount(len(columns))
            self.data_table.setHorizontalHeaderLabels(columns)
            
            # Add rows
            self.data_table.setRowCount(len(data))
            for row, record in enumerate(data):
                for col, value in enumerate(record.values()):
                    self.data_table.setItem(row, col, QTableWidgetItem(str(value)))
            
            # Auto-resize columns
            self.data_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _export_table(self):
        """Export table"""
        current_item = self.tables_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a table")
            return
        
        table_name = current_item.text()
        
        # File dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Table", f"{table_name}.json",
            "JSON Files (*.json);;CSV Files (*.csv);;SQL Files (*.sql)"
        )
        
        if not file_path:
            return
        
        try:
            data = self.explorer.export_table(table_name)
            
            if file_path.endswith('.json'):
                import json
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            elif file_path.endswith('.csv'):
                import csv
                if data:
                    with open(file_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
            
            QMessageBox.information(self, "Success", f"Exported {len(data)} records")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _open_query_dialog(self):
        """Open custom query dialog"""
        from PyQt6.QtWidgets import QDialog, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Execute Query")
        dialog.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        query_edit = QTextEdit()
        query_edit.setPlaceholderText("Enter SQL query...")
        layout.addWidget(query_edit)
        
        btn_layout = QHBoxLayout()
        execute_btn = QPushButton("Execute")
        result_text = QTextEdit()
        result_text.setReadOnly(True)
        
        def execute_query():
            query = query_edit.toPlainText()
            if not query:
                QMessageBox.warning(dialog, "Error", "Please enter a query")
                return
            
            try:
                success, result = self.explorer.execute_query(query)
                if success:
                    result_text.setText(str(result))
                else:
                    result_text.setText(f"Error: {result}")
            except Exception as e:
                result_text.setText(f"Error: {str(e)}")
        
        execute_btn.clicked.connect(execute_query)
        btn_layout.addWidget(execute_btn)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(result_text)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def _refresh_connection_status(self):
        """Refresh connection status display"""
        status = self.explorer.get_connection_status()
        # Status can be displayed in a status bar if needed
        pass
