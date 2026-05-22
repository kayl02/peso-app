# PESO Employment Application System
Group 7 — BSIT 2-1 — PUP CCIS

---

## How to Run the App

### Step 1 — Install Python requirements
```
pip install flask mysql-connector-python
```

### Step 2 — Set up the database
Open MySQL (Workbench, XAMPP, or terminal) and run:
```
source schema.sql
```
Or copy-paste the contents of `schema.sql` into your MySQL client.

### Step 3 — Update your DB password in app.py
Open `app.py` and find this block (around line 13):
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'secret',   # <-- change this to your MySQL password
    'database': 'peso_db'
}
```

### Step 4 — Run the app
```
python app.py
```

Then open your browser and go to:
```
http://localhost:5000
```

---

## Pages
| URL | Description |
|-----|-------------|
| / | Dashboard with stats |
| /applicants | List of all applicants |
| /apply | Submit new application form |
| /applicant/<id> | View full applicant details |
| /delete/<id> | Delete an applicant (POST) |
| /reports | All 10 SQL queries with live results |

---

## SQL Queries Summary
| # | Type | Query |
|---|------|-------|
| 1 | Simple | SELECT all applicants |
| 2 | Simple | INSERT new applicant (via form) |
| 3 | Simple | DELETE applicant |
| 4 | Moderate | SELECT with WHERE (filter by civil status) |
| 5 | Moderate | UPDATE employment status |
| 6 | Moderate | SELECT with JOIN (applicant + employer) |
| 7 | Moderate | SELECT with JOIN (applicant + languages) |
| 8 | Difficult | COUNT + GROUP BY (employment status stats) |
| 9 | Difficult | COUNT + GROUP BY + HAVING (multi-training applicants) |
| 10 | Difficult | JOIN + WHERE + IS NOT NULL (OFW with dependents) |
