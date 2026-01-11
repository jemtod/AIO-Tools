"""
Database Explorer Tool Module
Handles database connections and exploration
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod


class DatabaseConnection(ABC):
    """Abstract base class for database connections"""
    
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> Tuple[bool, any]:
        pass
    
    @abstractmethod
    def get_tables(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_table_schema(self, table_name: str) -> Dict:
        pass


class SQLiteConnection(DatabaseConnection):
    """SQLite database connection"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"SQLite connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        try:
            if self.connection:
                self.connection.close()
            return True
        except Exception as e:
            print(f"SQLite disconnection error: {e}")
            return False
    
    def execute_query(self, query: str) -> Tuple[bool, any]:
        try:
            self.cursor.execute(query)
            if query.strip().upper().startswith('SELECT'):
                return True, self.cursor.fetchall()
            else:
                self.connection.commit()
                return True, self.cursor.rowcount
        except Exception as e:
            return False, str(e)
    
    def get_tables(self) -> List[str]:
        try:
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching tables: {e}")
            return []
    
    def get_table_schema(self, table_name: str) -> Dict:
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            
            schema = {
                'columns': [
                    {
                        'name': col[1],
                        'type': col[2],
                        'not_null': bool(col[3]),
                        'default': col[4],
                        'primary_key': bool(col[5])
                    }
                    for col in columns
                ]
            }
            return schema
        except Exception as e:
            print(f"Error fetching schema: {e}")
            return {}
    
    def get_table_data(self, table_name: str, limit: int = 100) -> List[Dict]:
        try:
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            columns = [description[0] for description in self.cursor.description]
            rows = self.cursor.fetchall()
            
            return [
                {col: val for col, val in zip(columns, row)}
                for row in rows
            ]
        except Exception as e:
            print(f"Error fetching table data: {e}")
            return []
    
    def export_table(self, table_name: str) -> List[Dict]:
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            columns = [description[0] for description in self.cursor.description]
            rows = self.cursor.fetchall()
            
            return [
                {col: val for col, val in zip(columns, row)}
                for row in rows
            ]
        except Exception as e:
            print(f"Error exporting table: {e}")
            return []


class DatabaseExplorer:
    """Main database explorer tool class"""
    
    def __init__(self):
        self.current_connection = None
        self.connection_history = []
    
    def create_sqlite_connection(self, db_path: str) -> bool:
        """Create SQLite connection"""
        try:
            connection = SQLiteConnection(db_path)
            if connection.connect():
                self.current_connection = connection
                self.connection_history.append({
                    'type': 'SQLite',
                    'path': db_path,
                    'status': 'connected'
                })
                return True
            return False
        except Exception as e:
            print(f"Error creating connection: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect current connection"""
        if self.current_connection:
            return self.current_connection.disconnect()
        return False
    
    def get_tables(self) -> List[str]:
        """Get list of tables in current database"""
        if self.current_connection:
            return self.current_connection.get_tables()
        return []
    
    def get_table_info(self, table_name: str) -> Dict:
        """Get table schema and row count"""
        if not self.current_connection:
            return {}
        
        schema = self.current_connection.get_table_schema(table_name)
        
        # Get row count
        try:
            success, result = self.current_connection.execute_query(
                f"SELECT COUNT(*) FROM {table_name}"
            )
            row_count = result[0][0] if success and result else 0
        except:
            row_count = 0
        
        return {
            'name': table_name,
            'schema': schema,
            'row_count': row_count
        }
    
    def get_table_preview(self, table_name: str, limit: int = 100) -> List[Dict]:
        """Get preview of table data"""
        if self.current_connection:
            return self.current_connection.get_table_data(table_name, limit)
        return []
    
    def export_table(self, table_name: str) -> List[Dict]:
        """Export entire table data"""
        if self.current_connection:
            return self.current_connection.export_table(table_name)
        return []
    
    def execute_query(self, query: str) -> Tuple[bool, any]:
        """Execute custom SQL query"""
        if self.current_connection:
            return self.current_connection.execute_query(query)
        return False, "No connection"
    
    def get_connection_status(self) -> Dict:
        """Get current connection status"""
        if self.current_connection:
            return {
                'connected': True,
                'type': type(self.current_connection).__name__
            }
        return {'connected': False}
    
    def get_connection_history(self) -> List[Dict]:
        """Get connection history"""
        return self.connection_history
