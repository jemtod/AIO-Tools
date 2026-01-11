"""
Data Dumping Tool Module
Handles data extraction and export from various sources
"""

import json
import csv
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class DataDumper:
    """Main data dumping tool class"""
    
    def __init__(self):
        self.last_dump = None
        self.dump_history = []
        
    def export_to_json(self, data: List[Dict], filename: str) -> bool:
        """Export data to JSON format"""
        try:
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            self._record_dump("JSON", filename, len(data))
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def export_to_csv(self, data: List[Dict], filename: str) -> bool:
        """Export data to CSV format"""
        try:
            if not data:
                return False
                
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            self._record_dump("CSV", filename, len(data))
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_sql(self, data: List[Dict], table_name: str, 
                     filename: str) -> bool:
        """Export data to SQL INSERT statements"""
        try:
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                if not data:
                    return False
                
                columns = list(data[0].keys())
                f.write(f"-- Dumped at {datetime.now().isoformat()}\n\n")
                f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n")
                
                for i, row in enumerate(data):
                    values = []
                    for col in columns:
                        val = row.get(col)
                        if val is None:
                            values.append("NULL")
                        elif isinstance(val, str):
                            values.append(f"'{val.replace(chr(39), chr(39)*2)}'")
                        else:
                            values.append(str(val))
                    
                    separator = "," if i < len(data) - 1 else ";"
                    f.write(f"({', '.join(values)}){separator}\n")
            
            self._record_dump("SQL", filename, len(data))
            return True
        except Exception as e:
            print(f"Error exporting to SQL: {e}")
            return False
    
    def import_from_json(self, filename: str) -> Optional[List[Dict]]:
        """Import data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Error importing JSON: {e}")
            return None
    
    def import_from_csv(self, filename: str) -> Optional[List[Dict]]:
        """Import data from CSV file"""
        try:
            data = []
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            return data
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return None
    
    def filter_data(self, data: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter data based on criteria"""
        filtered = data
        for key, value in filters.items():
            filtered = [item for item in filtered if item.get(key) == value]
        return filtered
    
    def get_dump_history(self) -> List[Dict]:
        """Get history of dump operations"""
        return self.dump_history
    
    def _record_dump(self, format_type: str, filename: str, record_count: int):
        """Record dump operation in history"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'format': format_type,
            'filename': filename,
            'records': record_count
        }
        self.dump_history.append(record)
        self.last_dump = record
