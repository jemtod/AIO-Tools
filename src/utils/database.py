"""
Database utility functions
"""

from typing import Dict, Optional


class DatabaseConfig:
    """Database configuration helper"""
    
    def __init__(self):
        self.configs = {}
    
    def add_config(self, name: str, config: Dict) -> bool:
        """Add database configuration"""
        try:
            self.configs[name] = config
            return True
        except Exception as e:
            print(f"Error adding config: {e}")
            return False
    
    def get_config(self, name: str) -> Optional[Dict]:
        """Get database configuration"""
        return self.configs.get(name)
    
    def list_configs(self) -> list:
        """List all configurations"""
        return list(self.configs.keys())
    
    def delete_config(self, name: str) -> bool:
        """Delete database configuration"""
        if name in self.configs:
            del self.configs[name]
            return True
        return False


# Common database ports
DATABASE_PORTS = {
    'postgresql': 5432,
    'mysql': 3306,
    'mongodb': 27017,
    'redis': 6379,
    'sqlite': None,
    'mariadb': 3306,
    'oracle': 1521,
    'mssql': 1433
}


def get_default_port(db_type: str) -> Optional[int]:
    """Get default port for database type"""
    return DATABASE_PORTS.get(db_type.lower())
