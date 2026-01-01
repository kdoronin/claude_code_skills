#!/usr/bin/env python3
"""
Query Runner
============
Выполняет SQL-запросы и сохраняет результаты в файлы.
Поддерживает SQLite, PostgreSQL и MySQL базы данных.

Использование:
    # SQLite
    python query_runner.py --sqlite database.sqlite "SELECT * FROM users LIMIT 10"

    # PostgreSQL/MySQL (uses .env with DB_TYPE)
    python query_runner.py "SELECT * FROM users LIMIT 10"
    python query_runner.py -f query.sql -o my_report.csv

Форматы вывода:
    csv  - CSV файл (по умолчанию)
    xlsx - Excel файл
    json - JSON файл
    md   - Markdown таблица

Результаты сохраняются в папку output/reports/
"""

import os
import sys
import json
import argparse
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

# Load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OUTPUT_DIR = Path(__file__).parent / 'output' / 'reports'


def get_db_config(database_override=None):
    """Get database configuration from environment."""
    db_name = database_override or os.getenv('DB_NAME') or os.getenv('DB_DATABASE') or os.getenv('DATABASE') or 'app'
    db_type = (os.getenv('DB_TYPE') or 'mysql').lower()
    return {
        'type': db_type,
        'host': os.getenv('DB_IP') or os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'user': os.getenv('DB_USER') or os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD') or os.getenv('DB_PASS'),
        'database': db_name,
    }


def create_postgresql_connection(config):
    """Create PostgreSQL database connection."""
    try:
        import psycopg2
        connection = psycopg2.connect(
            host=config['host'],
            port=config['port'] or 5432,
            user=config['user'],
            password=config['password'],
            dbname=config['database']
        )
        return connection, 'postgresql'
    except ImportError:
        print("Ошибка: psycopg2 не установлен. Выполните: pip install psycopg2-binary")
        return None, None
    except Exception as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")
        return None, None


def create_mysql_connection(config):
    """Create MySQL database connection."""
    try:
        import mysql.connector
        connection = mysql.connector.connect(
            host=config['host'],
            port=config['port'] or 3306,
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection, 'mysql'
    except Exception as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None, None


def create_sqlite_connection(filepath):
    """Create SQLite database connection."""
    try:
        if not Path(filepath).exists():
            print(f"Ошибка: SQLite файл не найден: {filepath}")
            return None, None
        connection = sqlite3.connect(filepath)
        connection.row_factory = sqlite3.Row
        return connection, 'sqlite'
    except Exception as e:
        print(f"Ошибка подключения к SQLite: {e}")
        return None, None


def execute_query(connection, query, db_type):
    """Execute query and return results with column names."""
    try:
        if db_type == 'postgresql':
            import psycopg2.extras
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
        elif db_type == 'mysql':
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
        else:  # sqlite
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            results = [dict(row) for row in rows]

        return columns, results
    except Exception as e:
        print(f"Ошибка выполнения запроса: {e}")
        return [], []


def save_csv(columns, results, filepath):
    """Save results to CSV file."""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)


def save_json(columns, results, filepath):
    """Save results to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str, ensure_ascii=False)


def save_markdown(columns, results, filepath):
    """Save results to Markdown table."""
    with open(filepath, 'w', encoding='utf-8') as f:
        if not results:
            f.write("*Нет данных*\n")
            return

        # Header
        f.write("| " + " | ".join(columns) + " |\n")
        f.write("|" + "|".join(["---"] * len(columns)) + "|\n")

        # Rows
        for row in results:
            values = [str(row.get(col, ""))[:100] for col in columns]
            f.write("| " + " | ".join(values) + " |\n")


def save_xlsx(columns, results, filepath):
    """Save results to Excel file."""
    try:
        import openpyxl
        from openpyxl import Workbook
    except ImportError:
        print("Для Excel формата установите: pip install openpyxl")
        print("Сохраняю в CSV вместо Excel...")
        csv_path = filepath.with_suffix('.csv')
        save_csv(columns, results, csv_path)
        return csv_path

    wb = Workbook()
    ws = wb.active

    # Header
    ws.append(columns)

    # Data
    for row in results:
        ws.append([row.get(col) for col in columns])

    # Auto-adjust column widths
    for col_idx, column in enumerate(columns, 1):
        max_length = len(str(column))
        for row in results[:100]:
            cell_value = str(row.get(column, ""))
            max_length = max(max_length, min(len(cell_value), 50))
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = max_length + 2

    wb.save(filepath)
    return filepath


def generate_filename(output_format):
    """Generate unique filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"report_{timestamp}.{output_format}"


def main():
    parser = argparse.ArgumentParser(
        description='Query Runner - выполняет SQL и сохраняет в файл',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # SQLite
  python query_runner.py --sqlite database.sqlite "SELECT * FROM users LIMIT 10"

  # PostgreSQL/MySQL (credentials из .env, DB_TYPE определяет тип)
  python query_runner.py "SELECT * FROM users LIMIT 10"
  python query_runner.py -f my_query.sql -o users.csv
  python query_runner.py "SELECT status, COUNT(*) FROM orders GROUP BY status" --format xlsx
        """
    )
    parser.add_argument('query', nargs='?', help='SQL запрос для выполнения')
    parser.add_argument('-f', '--file', help='SQL файл для выполнения')
    parser.add_argument('-o', '--output', help='Имя выходного файла')
    parser.add_argument('--format', choices=['csv', 'xlsx', 'json', 'md'], default='csv',
                        help='Формат вывода (по умолчанию: csv)')
    parser.add_argument('--sqlite', '-s', metavar='PATH',
                        help='Путь к SQLite файлу (без логина/пароля)')
    parser.add_argument('-d', '--database', help='Имя базы данных')
    parser.add_argument('--print', action='store_true', help='Также вывести результат в консоль')

    args = parser.parse_args()

    # Get query
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            query = f.read()
    elif args.query:
        query = args.query
    else:
        parser.print_help()
        sys.exit(1)

    # Create connection based on type
    if args.sqlite:
        connection, db_type = create_sqlite_connection(args.sqlite)
        db_name = Path(args.sqlite).stem
    else:
        config = get_db_config(args.database)
        db_name = config['database']
        if config['type'] == 'postgresql':
            connection, db_type = create_postgresql_connection(config)
        else:  # mysql/mariadb
            connection, db_type = create_mysql_connection(config)

    if not connection:
        sys.exit(1)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        print(f"Выполняю запрос к базе '{db_name}' ({db_type.upper()})...")
        columns, results = execute_query(connection, query, db_type)

        if not results:
            print("Запрос выполнен, но не вернул данных.")
            return

        print(f"Получено строк: {len(results)}")

        # Determine output filename
        if args.output:
            filename = args.output
            if not filename.endswith(f'.{args.format}'):
                filename = f"{filename}.{args.format}"
        else:
            filename = generate_filename(args.format)

        filepath = OUTPUT_DIR / filename

        # Save results
        if args.format == 'csv':
            save_csv(columns, results, filepath)
        elif args.format == 'json':
            save_json(columns, results, filepath)
        elif args.format == 'md':
            save_markdown(columns, results, filepath)
        elif args.format == 'xlsx':
            filepath = save_xlsx(columns, results, filepath)

        print(f"Результат сохранён: {filepath}")

        # Print preview if requested
        if args.print:
            print("\nПревью (первые 10 строк):")
            print("-" * 80)
            for i, row in enumerate(results[:10]):
                print(row)
            if len(results) > 10:
                print(f"... и ещё {len(results) - 10} строк")

    finally:
        connection.close()


if __name__ == '__main__':
    main()
