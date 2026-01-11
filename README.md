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

### 5. **Database Dumper (Dump SQL)**
   - Extract database schema from vulnerable SQL injection URLs
   - Search and dump data by keywords (user, password, email, etc.)
   - Retrieve database metadata (version, current user, database name)
   - UNION-based SQL injection exploitation
   - Support for MySQL and compatible databases
   - Export dumped data to TXT or CSV format
   - Real-time results display with column preview
   - Automatic keyword matching across all tables and columns

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
python run.py
```

### Database Dumper (Dump SQL Tab)

The Database Dumper tool allows you to extract data from vulnerable SQL injection targets.

#### Basic Workflow:

1. **Get DB Info & Schema**
   - Enter target URL: `http://example.com/page.php?id=1`
   - Click "Get DB Info & Schema"
   - View database version, current user, and table/column structure

2. **Dump by Keywords**
   - Modify keywords if needed (default: user, pass, email, password, username, admin, login)
   - Click "Dump by Keywords"
   - Results display matching columns with record count and data preview

3. **Export Results**
   - Click "Export Results"
   - Choose TXT or CSV format
   - Save dumped data to file

#### Example:

```
Target URL: http://vulnerable-site.com/products.php?id=1
Keywords: user, pass, email, password

Results:
- users.username (25 records)
- users.password (25 records)  
- users.email (25 records)
- admin_users.user (5 records)
```

#### Keyword Search Examples:

- **User Credentials**: user, pass, password, username, admin, login
- **Personal Info**: email, phone, name, address, ssn
- **Payment Info**: card, credit, banking, account, balance
- **API Keys**: token, key, secret, api_key, auth

#### Tips:

- Start with "Get DB Info & Schema" to understand database structure
- Use common keyword patterns for better results
- Export data for offline analysis
- Test on one URL first before bulk operations

## Requirements

- Python 3.8+
- PyQt6 for GUI
- Database drivers for PostgreSQL, MySQL, MongoDB
- Various security and networking libraries

## License

Jemtod - 2026

## Author

Created for personal use and security testing purposes.

---

**Note**: Use responsibly and only on systems you have permission to test.
