#!/usr/bin/env python3
"""
Database Discovery Tool
=======================
Автоматически находит все доступные базы данных:
- SQLite файлы в папке database/
- MySQL базы из .env

Использование:
    python list_databases.py          # Список доступных БД
    python list_databases.py --json   # В формате JSON
    python list_databases.py --setup  # Извлечь схемы всех БД
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROJECT_DIR = Path(__file__).parent
DATABASE_DIR = PROJECT_DIR / 'database'
OUTPUT_DIR = PROJECT_DIR / 'output'


def get_sqlite_databases():
    """Find all SQLite databases in database/ folder."""
    databases = []

    if not DATABASE_DIR.exists():
        return databases

    for file in DATABASE_DIR.iterdir():
        if file.suffix.lower() in ['.sqlite', '.sqlite3', '.db']:
            # Get file size
            size_mb = file.stat().st_size / (1024 * 1024)

            # Try to get table count
            table_count = 0
            try:
                import sqlite3
                conn = sqlite3.connect(str(file))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                table_count = cursor.fetchone()[0]
                conn.close()
            except:
                pass

            databases.append({
                'type': 'sqlite',
                'name': file.stem,
                'path': f"database/{file.name}",
                'full_path': str(file),
                'size_mb': round(size_mb, 2),
                'tables': table_count,
                'run_command': f"python query_runner.py --sqlite database/{file.name}",
                'extract_command': f"python db_extractor.py --sqlite database/{file.name}"
            })

    return databases


def get_mysql_databases():
    """Check if MySQL credentials are available in .env."""
    databases = []

    host = os.getenv('DB_IP') or os.getenv('DB_HOST')
    user = os.getenv('DB_USER') or os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD') or os.getenv('DB_PASS')
    db_name = os.getenv('DB_NAME') or os.getenv('DB_DATABASE')

    if not host or not user:
        return databases

    # Try to connect and list databases
    try:
        import mysql.connector

        # If specific database is set, add it
        if db_name:
            databases.append({
                'type': 'mysql',
                'name': db_name,
                'host': host,
                'run_command': f"python query_runner.py",
                'extract_command': f"python db_extractor.py --database {db_name}"
            })
        else:
            # List available databases
            conn = mysql.connector.connect(host=host, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            skip = ['information_schema', 'performance_schema', 'mysql', 'sys']
            for (db,) in cursor.fetchall():
                if db.lower() not in skip:
                    databases.append({
                        'type': 'mysql',
                        'name': db,
                        'host': host,
                        'run_command': f"python query_runner.py --database {db}",
                        'extract_command': f"python db_extractor.py --database {db}"
                    })
            conn.close()
    except Exception as e:
        # If can't connect but credentials exist, still show configured DB
        if db_name:
            databases.append({
                'type': 'mysql',
                'name': db_name,
                'host': host,
                'error': str(e),
                'run_command': f"python query_runner.py",
                'extract_command': f"python db_extractor.py --database {db_name}"
            })

    return databases


def get_all_databases():
    """Get all available databases."""
    databases = []
    databases.extend(get_sqlite_databases())
    databases.extend(get_mysql_databases())
    return databases


def check_schema_exists(db_info):
    """Check if schema has been extracted for this database."""
    schema_file = OUTPUT_DIR / 'databases' / db_info['name'] / 'schema_info.json'
    return schema_file.exists()


def setup_all_databases():
    """Extract schema for all databases."""
    import subprocess

    databases = get_all_databases()

    if not databases:
        print("No databases found!")
        return

    for db in databases:
        print(f"\n=== Setting up {db['name']} ({db['type'].upper()}) ===")
        cmd = db['extract_command']
        print(f"Running: {cmd}")
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {db['name']} setup complete")
        else:
            print(f"✗ Error setting up {db['name']}: {result.stderr}")


def main():
    parser = argparse.ArgumentParser(description='Database Discovery Tool')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--setup', action='store_true', help='Extract schema for all databases')
    args = parser.parse_args()

    if args.setup:
        setup_all_databases()
        return

    databases = get_all_databases()

    if args.json:
        print(json.dumps(databases, indent=2, ensure_ascii=False))
        return

    if not databases:
        print("No databases found!")
        print("\nTo add databases:")
        print("  SQLite: Put .sqlite files in database/ folder")
        print("  MySQL:  Configure .env with DB_HOST, DB_USER, DB_PASSWORD")
        return

    print("Available databases:\n")

    for db in databases:
        print(f"  [{db['type'].upper()}] {db['name']}")
        if db['type'] == 'sqlite':
            print(f"         Path: {db['path']}")
            print(f"         Size: {db['size_mb']} MB, Tables: {db['tables']}")
        else:
            print(f"         Host: {db.get('host', 'N/A')}")
        print(f"         Run:  {db['run_command']}")
        print()


if __name__ == '__main__':
    main()
