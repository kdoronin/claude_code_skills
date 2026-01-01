#!/usr/bin/env python3
"""
SQL Helper
==========
Interactive helper for running SQL queries against MySQL or SQLite databases.
Useful for quick queries and testing.

Usage:
    # SQLite
    python sql_helper.py --sqlite database.sqlite "SELECT * FROM users LIMIT 5"
    python sql_helper.py --sqlite database.sqlite -i

    # MySQL
    python sql_helper.py "SELECT * FROM users LIMIT 5"
    python sql_helper.py --file query.sql
    python sql_helper.py --interactive
"""

import os
import sys
import json
import argparse
import sqlite3
from pathlib import Path

# Load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_mysql_config(database_override=None):
    """Get MySQL configuration from environment."""
    db_name = database_override or os.getenv('DB_NAME') or os.getenv('DB_DATABASE') or os.getenv('DATABASE') or 'app'
    return {
        'host': os.getenv('DB_IP') or os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER') or os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD') or os.getenv('DB_PASS'),
        'database': db_name,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }


def create_mysql_connection(config):
    """Create MySQL database connection."""
    try:
        import mysql.connector
        connection = mysql.connector.connect(**config)
        return connection, 'mysql'
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None, None


def create_sqlite_connection(filepath):
    """Create SQLite database connection."""
    try:
        if not Path(filepath).exists():
            print(f"Error: SQLite file not found: {filepath}")
            return None, None
        connection = sqlite3.connect(filepath)
        connection.row_factory = sqlite3.Row
        return connection, 'sqlite'
    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
        return None, None


def run_query(connection, query, db_type, output_format='table'):
    """Execute query and return formatted results."""
    try:
        if db_type == 'mysql':
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            if cursor.description:
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
            else:
                connection.commit()
                return f"Query executed. Rows affected: {cursor.rowcount}"
        else:  # sqlite
            cursor = connection.cursor()
            cursor.execute(query)

            if cursor.description:
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                results = [dict(row) for row in rows]
            else:
                connection.commit()
                return f"Query executed. Rows affected: {cursor.rowcount}"

        if output_format == 'json':
            return json.dumps(results, indent=2, default=str)
        elif output_format == 'csv':
            lines = [','.join(columns)]
            for row in results:
                lines.append(','.join(str(row.get(col, '')) for col in columns))
            return '\n'.join(lines)
        else:  # table format
            if not results:
                return "No results."

            # Calculate column widths
            widths = {col: len(col) for col in columns}
            for row in results[:100]:
                for col in columns:
                    val = str(row.get(col, ''))[:50]
                    widths[col] = max(widths[col], len(val))

            # Build table
            header = ' | '.join(col.ljust(widths[col])[:50] for col in columns)
            separator = '-+-'.join('-' * min(widths[col], 50) for col in columns)
            lines = [header, separator]

            for row in results[:100]:
                line = ' | '.join(str(row.get(col, '')).ljust(widths[col])[:50] for col in columns)
                lines.append(line)

            if len(results) > 100:
                lines.append(f"... and {len(results) - 100} more rows")

            return '\n'.join(lines)

    except Exception as e:
        return f"Error: {e}"


def interactive_mode(connection, db_type, db_name):
    """Run interactive SQL session."""
    print(f"SQL Helper - Interactive Mode")
    print(f"Database: {db_name} ({db_type.upper()})")
    print("Type 'exit' or 'quit' to exit")
    print("Type 'json' or 'csv' or 'table' to change output format")
    print("-" * 50)

    output_format = 'table'

    while True:
        try:
            query = input("\nsql> ").strip()

            if not query:
                continue

            if query.lower() in ('exit', 'quit'):
                break

            if query.lower() == 'json':
                output_format = 'json'
                print("Output format: JSON")
                continue

            if query.lower() == 'csv':
                output_format = 'csv'
                print("Output format: CSV")
                continue

            if query.lower() == 'table':
                output_format = 'table'
                print("Output format: Table")
                continue

            result = run_query(connection, query, db_type, output_format)
            print(result)

        except KeyboardInterrupt:
            print("\nExiting...")
            break


def main():
    parser = argparse.ArgumentParser(
        description='SQL Helper - interactive SQL tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # SQLite
  python sql_helper.py --sqlite database.sqlite "SELECT * FROM users"
  python sql_helper.py --sqlite database.sqlite -i

  # MySQL
  python sql_helper.py "SELECT * FROM users"
  python sql_helper.py -i
        """
    )
    parser.add_argument('query', nargs='?', help='SQL query to execute')
    parser.add_argument('--file', '-f', help='SQL file to execute')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--format', '-o', choices=['table', 'json', 'csv'], default='table',
                        help='Output format')
    parser.add_argument('--sqlite', '-s', metavar='PATH',
                        help='Path to SQLite database file')
    parser.add_argument('-d', '--database', help='MySQL database name')

    args = parser.parse_args()

    # Create connection based on type
    if args.sqlite:
        connection, db_type = create_sqlite_connection(args.sqlite)
        db_name = Path(args.sqlite).stem
    else:
        config = get_mysql_config(args.database)
        connection, db_type = create_mysql_connection(config)
        db_name = config['database']

    if not connection:
        print("Failed to connect to database.")
        sys.exit(1)

    try:
        if args.interactive:
            interactive_mode(connection, db_type, db_name)
        elif args.file:
            with open(args.file, 'r') as f:
                query = f.read()
            print(run_query(connection, query, db_type, args.format))
        elif args.query:
            print(run_query(connection, args.query, db_type, args.format))
        else:
            parser.print_help()
    finally:
        connection.close()


if __name__ == '__main__':
    main()
