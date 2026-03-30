---
name: text-to-sql
description: "Sets up text-to-SQL projects and converts natural language questions into SQL queries for SQLite, PostgreSQL, MySQL, and MariaDB. Use when the user wants to query a database using natural language, set up a text-to-sql project, extract data from a .sqlite/.db file, or work with database credentials to analyze data."
---

# Text-to-SQL Skill

Convert natural language questions into SQL queries and execute them against SQL databases.

## Phase 1: Project Setup

### Step 1: Ask about database connection

**SQLite** (file-based, no credentials needed): User provides path to `.sqlite` or `.db` file, or places it in `database/`.

**Server database** (PostgreSQL, MySQL, MariaDB): User creates `.env` with connection details.

### Step 2: Initialize project

```bash
python scripts/init_project.py --target /path/to/project
```

Or manually: `mkdir -p database output/queries output/reports`, copy `scripts/*.py` and `assets/*` to project root, then `pip install -r requirements.txt`.

### Step 3: Configure and extract schema

**SQLite:**
```bash
python db_extractor.py --sqlite database/YOUR_DB.sqlite
```

**Server database:**
```bash
cp example.env .env  # Edit with actual credentials
python db_extractor.py --database your_database_name
```

### Step 4: Verify setup

Confirm these files exist in `output/`: `connection.json`, `text_to_sql_context.md`, `schema_info.json`, `database_documentation.md`.

---

## Phase 2: Query Workflow

### Step 1: Read schema context

Read `output/text_to_sql_context.md` for tables, columns, types, relationships, and enum values.

### Step 2: Generate SQL

Create SQL based on the user's question. See [references/sql_patterns.md](references/sql_patterns.md) for common patterns. Save to `output/queries/descriptive_name.sql`.

### Step 3: Execute

```bash
# SQLite
python query_runner.py --sqlite database/DB.sqlite -f output/queries/query.sql -o result.csv

# Server database
python query_runner.py -f output/queries/query.sql -o result.csv
```

If the query fails: check the error message, fix the SQL (common issues: wrong column names, missing JOINs, type mismatches), and re-execute.

### Step 4: Report results

Tell user: "Results saved to `output/reports/result.csv`"

Output formats: `--format csv` (default), `--format xlsx`, `--format json`, `--format md`
