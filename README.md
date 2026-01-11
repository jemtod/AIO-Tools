# DumpTools - Multi-Purpose Security & Data Tools Suite

A comprehensive Python-based GUI application for data dumping, security testing, and database exploration.

## Features

### 1. **Data Dumping Tool**
   - Export data from various sources (files, databases, APIs)
   - Multiple export formats (JSON, CSV, XML, SQL)
   - Batch operations support
   - Data filtering and transformation

### 2. **Security Testing Tool**
   - Network scanning and port discovery
   - Vulnerability assessment
   - Password strength analyzer
   - Hash generation and verification
   - SSL/TLS certificate checker
   - Web security headers analyzer

### 3. **Database Explorer**
   - Support for PostgreSQL, MySQL, MongoDB, SQLite
   - Database browsing and schema inspection
   - Query execution interface
   - Data preview and export
   - Connection management

### 4. **Dork Scanner & SQL Injection Finder**
   - Google dork list management
   - Load custom or default dork lists
   - SQL injection pattern detection in URLs
   - SQL injection payload testing
   - SQL error message detection
   - Bulk URL vulnerability scanning
   - Vulnerable URL collection and export (TXT/CSV)

## Project Structure

```
dumptools/
├── src/
│   ├── main.py                 # Application entry point
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── data_dumper.py      # Data dumping functionality
│   │   ├── security_tester.py  # Security testing tools
│   │   └── db_explorer.py      # Database exploration
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window
│   │   ├── dumper_ui.py        # Data dumper interface
│   │   ├── security_ui.py      # Security tester interface
│   │   └── db_explorer_ui.py   # Database explorer interface
│   └── utils/
│       ├── __init__.py
│       ├── database.py         # Database connection utilities
│       ├── security.py         # Security utilities
│       └── logger.py           # Logging configuration
├── assets/                     # Images, icons, stylesheets
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

1. Clone or download the repository
2. Install Python 3.8 or higher
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python src/main.py
```

## Requirements

- Python 3.8+
- PyQt6 for GUI
- Database drivers for PostgreSQL, MySQL, MongoDB
- Various security and networking libraries

## License

Personal Project - 2026

## Author

Created for personal use and security testing purposes.

---

**Note**: Use responsibly and only on systems you have permission to test.
