# Database Dumper Feature Documentation

## Overview

The **Database Dumper (Dump SQL)** tab has been added to the AIO TOOLS application, allowing security researchers to extract sensitive data from vulnerable SQL injection endpoints.

## Features

### 1. Database Information Retrieval
- **Get Database Version**: Retrieve MySQL/MariaDB version information
- **Get Current User**: Identify the database user
- **Get Database Name**: Determine active database
- **Get Schema**: Extract table names and column information

### 2. Keyword-Based Data Dumping
Search and extract database columns matching specific keywords:

**Default Keywords**:
- `user`, `pass`, `email`, `password`, `username`, `admin`, `login`

**Customizable**: Modify keywords for specific targets
- Payment info: `card`, `credit`, `banking`, `account`
- Personal data: `phone`, `name`, `address`, `ssn`
- Authentication: `token`, `key`, `secret`, `api_key`

### 3. Results Management
- **Multiple Views**: Database Info, Schema, Dumped Data, Log
- **Data Preview**: See sample values in result tables
- **Tooltips**: Hover to see additional records
- **Export**: Save results as TXT or CSV format

## How to Use

### Step 1: Input Target URL
```
Example: http://example.com/products.php?id=1
```

### Step 2: Get Database Information
Click **"Get DB Info & Schema"** to retrieve:
- Database version and metadata
- Complete schema with all tables and columns

### Step 3: Configure Search Keywords
Modify the keywords field with terms to search for:
```
user,pass,email,password,username,admin,login
```

### Step 4: Execute Database Dump
Click **"Dump by Keywords"** to extract matching column data:
- Scans all tables
- Finds columns matching keywords
- Extracts up to 50 records per column
- Displays results in real-time

### Step 5: Export Results
Click **"Export Results"** to save data:
- **TXT Format**: Human-readable text file with clear organization
- **CSV Format**: Structured data for spreadsheet applications

## Technical Implementation

### Backend: `src/tools/sql_dumper.py`

**Key Classes & Methods**:

```python
class SQLDumper:
    # Extract database metadata
    def get_database_info(url: str) -> Dict
    
    # Get complete schema
    def extract_database_schema(url: str) -> Dict[str, List]
    
    # Search and dump by keywords
    def dump_database_by_keyword(url: str, keywords: List[str]) -> Dict
    
    # Export dumped data
    def export_dump_to_file(data: Dict, filename: str, format: str) -> bool
```

**SQL Injection Methods Used**:
- UNION-based injection for schema extraction
- information_schema queries for table/column enumeration
- GROUP_CONCAT for data aggregation

### Frontend: `src/ui/dork_scanner_ui.py`

**UI Components**:
- Input fields for URL and keywords
- Tabbed interface for results organization
- Result table with sortable columns
- Export and clear buttons
- Real-time status updates

## Workflow Integration

The Database Dumper integrates seamlessly with the SQL Injection scanner:

```
1. Dork Scanner (Google Dorking)
   ↓
2. SQL Injection Scanner (Find vulnerable URLs)
   ↓
3. Database Dumper (Extract data from vulnerabilities)
   ↓
4. Export & Analysis
```

## Supported Databases

- **MySQL** 4.0 - 8.0+
- **MariaDB** 10.x+
- **Percona Server** (MySQL-compatible)
- Other MySQL-compatible databases

## Results Tab Breakdown

### Database Info Tab
Shows:
- Database version
- Current user
- Active database name
- Connection details

### Schema Tab
Displays:
- All table names
- Column names per table
- Column count statistics

### Dumped Data Tab
Contains:
- Column name (table.column format)
- Record count
- Data preview with tooltip expansion

### Log Tab
Shows:
- Operation status
- Error messages
- SQL queries executed
- Processing timestamps

## Example Workflow

### Scenario: E-commerce Website Vulnerability

**Target**: `https://shop.example.com/products.php?id=1`

**Step 1**: Database Info
```
Database: MySQL 5.7.30
User: web_user@localhost
Active DB: shop_db
```

**Step 2**: Schema Retrieved
```
TABLE: users
  Columns: id, username, password, email, phone

TABLE: orders
  Columns: id, user_id, total, card_number, cvv

TABLE: admin
  Columns: id, admin_user, admin_pass
```

**Step 3**: Keyword Dump
```
Keywords: user, pass, email, card

Results:
- users.username (42 records)
- users.password (42 records)
- users.email (42 records)
- orders.card_number (128 records)
```

**Step 4**: Export Results
- File: `database_dump.txt` or `database_dump.csv`
- Contains all extracted data
- Organized by column

## Security & Legal Considerations

⚠️ **DISCLAIMER**: This tool is for authorized security testing only.

- Use only on systems you own or have explicit written permission to test
- Unauthorized access to computer systems is illegal
- Data obtained should be handled according to security policies
- Comply with GDPR, CCPA, and other data protection regulations

## Troubleshooting

### No Results Returned
- Verify the URL is actually vulnerable to SQL injection
- Check that the injectable parameter is correctly identified
- Try "Get DB Info & Schema" first to diagnose issues
- Ensure target database is MySQL-compatible

### Timeout Errors
- Increase timeout in network settings
- Target may be rate-limiting requests
- Try with fewer keywords first
- Check proxy settings if configured

### Special Characters in Data
- Results are UTF-8 encoded
- CSV format handles special characters automatically
- TXT format may need special text editor for viewing

## Performance Notes

- Dumping is rate-limited at 0.5 seconds between column extractions
- Default limit: 50 records per column
- Large dumps (1000+ records) may take several minutes
- Export to CSV for better handling of large datasets

## Export Format Details

### TXT Format
```
============================================================
Column: users.username
Records: 25
============================================================
admin
user1
user2
...
```

### CSV Format
```
# Column: users.username
admin
user1
user2
...

# Column: users.email
admin@example.com
...
```

## Integration with Other Tools

**From SQL Injection Scanner**:
- Click "Go to Dumper" on vulnerable URL results
- Automatically populates target URL in Dump SQL tab

**From Dork Scanner**:
- Auto-navigation available after dork scan completes
- URLs can be transferred to SQL Injection scanner
- Then to Database Dumper for exploitation chain

## Future Enhancements

Planned features:
- [ ] Time-based blind SQLi support
- [ ] Error-based SQLi support
- [ ] Boolean-based SQLi detection
- [ ] Stacked queries execution
- [ ] Custom payload builder
- [ ] Session/cookie management
- [ ] Multi-threading for parallel dumps
- [ ] Database firewall evasion techniques
- [ ] Scheduled automated dumps
- [ ] Web UI for remote testing

## Version History

### v1.0 (Current)
- Initial Database Dumper implementation
- UNION-based SQL injection support
- Schema extraction and enumeration
- Keyword-based column searching
- TXT/CSV export formats
- Integration with Dork Scanner and SQLi Scanner

## Support & Contributing

For issues, feature requests, or contributions:
- GitHub: https://github.com/jemtod/AIO-Tools
- License: MIT (see LICENSE file)
- Author: Jemtod (2026)

---

**Last Updated**: January 11, 2026
**Application Version**: AIO TOOLS v1.0
