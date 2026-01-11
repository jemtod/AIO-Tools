# Database Dumper - Quick Reference

## UI Layout

```
┌─────────────────────────────────────────────────────────┐
│ Dump SQL Tab                                             │
├─────────────────────────────────────────────────────────┤
│ Target URL: [http://example.com/page.php?id=1        ] │
│ Keywords:   [user,pass,email,password,username      ] │
│ [Get DB Info & Schema] [Dump by Keywords] [Export]   │
│                                                         │
│ ┌──────────────────────────────────────────────────┐   │
│ │ Tabs: Database Info | Schema | Dumped Data | Log│   │
│ ├──────────────────────────────────────────────────┤   │
│ │ Results display here...                          │   │
│ │                                                  │   │
│ │ Column          Records    Data                  │   │
│ │ users.user      42         admin|user1|user2...  │   │
│ │ users.password  42         hash1|hash2|...       │   │
│ │ users.email     42         a@b.com|c@d.com|...   │   │
│ └──────────────────────────────────────────────────┘   │
│ Status: Successfully dumped 3 columns                   │
└─────────────────────────────────────────────────────────┘
```

## Workflow

```
INPUT URL
   ↓
GET DB INFO & SCHEMA (Check if vulnerable)
   ↓
CONFIGURE KEYWORDS (Customize search terms)
   ↓
DUMP BY KEYWORDS (Extract matching data)
   ↓
EXPORT RESULTS (Save to file)
```

## Default Keywords

```
user, pass, email, password, username, admin, login
```

Add more based on target:
- **Authentication**: token, key, secret, auth, password, pwd
- **Personal**: name, phone, address, ssn, dob, nationality
- **Payment**: card, credit, banking, account, balance, cvv
- **Business**: company, api, secret, token, key, credential
```

## Tab Descriptions

| Tab | Purpose |
|-----|---------|
| **Database Info** | Shows version, current user, database name |
| **Schema** | Lists all tables and their columns |
| **Dumped Data** | Shows extracted records with counts |
| **Log** | Operation status and error messages |

## Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Get DB Info | Click "Get DB Info & Schema" |
| Start Dump | Click "Dump by Keywords" |
| Export | Click "Export Results" |
| Clear | Click "Clear Results" |

## Export Formats

### TXT (Human-readable)
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

### CSV (Spreadsheet-compatible)
```
# Column: users.username
admin
user1
user2
```

## Typical Results

```
FOUND COLUMNS:
✓ users.username (45 records)
✓ users.password (45 records)
✓ users.email (45 records)
✓ admin.adminuser (3 records)
✓ admin.adminpass (3 records)

TOTAL: 5 columns, 141 records
```

## Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| No results | URL not vulnerable | Test with SQLi scanner first |
| Timeout | Slow target | Increase timeout in settings |
| Invalid URL | Bad format | Use: http://site.com/page.php?id=1 |
| No schema | Different DB | May not be MySQL-compatible |

## Example URLs to Test

```
http://example.com/page.php?id=1
http://example.com/products.php?product_id=1
http://example.com/search.php?q=test
http://example.com/user.php?username=admin
http://example.com/post.php?post_id=1
```

## Tips & Tricks

1. **Start Small**: Test with 3-4 keywords first
2. **Check Schema First**: Run "Get DB Info & Schema" before dumping
3. **Customize Keywords**: Modify based on target (ecommerce vs social media)
4. **Export Early**: Save results as you go
5. **Rate Limit**: Tool adds 0.5s delay between queries to avoid detection
6. **Encoding**: UTF-8 compatible, handles special characters

## Integration Points

From **SQL Injection Scanner**:
- Right-click on vulnerable URL
- Select "Go to Dumper" option
- URL auto-populated in Dump SQL tab

From **Dork Scanner**:
- Complete dork scan
- Dialog offers auto-navigation to SQL Injection scanner
- Once vulnerable URLs found, navigate to Dump SQL tab

## Data Privacy

⚠️ **IMPORTANT**: 
- Only dump data you're authorized to access
- Keep dumps secure and encrypted
- Delete dumps after analysis
- Follow GDPR/CCPA compliance

## Common Keyword Sets

### E-Commerce
```
user,pass,email,password,card,cvv,order,address,phone
```

### Social Network
```
user,email,phone,name,password,token,session,bio
```

### Bank/Finance
```
account,balance,card,cvv,password,pin,user,email
```

### Web Application
```
user,admin,password,token,key,secret,api,config,database
```

### CMS/Blog
```
user,pass,password,email,admin,token,key,post,content
```

## Status Indicators

| Status | Meaning |
|--------|---------|
| Ready | Waiting for input |
| Fetching... | Retrieving database info |
| Dumping... | Extracting data |
| Success | Operation completed |
| Error | Check Log tab for details |

## Export File Sizes

- **Small dump** (< 100 records): ~5-20 KB
- **Medium dump** (100-1000 records): ~20-100 KB
- **Large dump** (1000+ records): 100+ KB

Recommend CSV for large exports (more compact).

## Security Best Practices

✓ Do:
- [ ] Use on authorized systems only
- [ ] Enable HTTPS for target connections
- [ ] Secure exported data
- [ ] Document testing scope
- [ ] Log all activity

✗ Don't:
- [ ] Share dumps with unauthorized people
- [ ] Leave dumps on shared computers
- [ ] Test without permission
- [ ] Modify data through this tool
- [ ] Share credentials obtained

---

**Quick Start**: Enter URL → Click "Get DB Info" → Modify keywords → Click "Dump" → Export results
