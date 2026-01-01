#!/usr/bin/env python3
"""
Universal Database Schema Extractor
====================================
Connects to SQL databases and extracts schema information for text-to-sql tasks.

Supports:
- SQLite: via path to .sqlite/.db file (no credentials needed)
- PostgreSQL: via credentials in .env file (DB_TYPE=postgresql)
- MySQL/MariaDB: via credentials in .env file (DB_TYPE=mysql)

Usage:
    # SQLite
    python db_extractor.py --sqlite path/to/database.sqlite

    # PostgreSQL/MySQL (uses .env)
    python db_extractor.py --database your_db_name
    python db_extractor.py --list-databases

Output:
    - output/schema_info.json - Complete schema in JSON format
    - output/database_documentation.md - Human-readable documentation
    - output/text_to_sql_context.md - Optimized context for LLM text-to-sql
    - output/cursor_instructions.md - Instructions for Cursor to generate examples
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod

# Load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OUTPUT_DIR = Path(__file__).parent / 'output'

# Configuration for analysis
CONFIG = {
    'enum_max_distinct': 50,
    'enum_min_rows': 10,
    'json_sample_size': 10,
    'enum_max_value_length': 100,
    'skip_tables_patterns': ['information_schema', 'performance_schema', 'mysql', 'sys'],
    'enum_column_types': ['varchar', 'char', 'text', 'enum', 'set'],
    'json_column_types': ['json', 'longtext', 'mediumtext', 'text'],
}


# =============================================================================
# Database Abstraction Layer
# =============================================================================

class DatabaseConnection(ABC):
    """Abstract base class for database connections."""

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def execute(self, query):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_tables_info(self):
        pass

    @abstractmethod
    def get_columns_info(self):
        pass

    @abstractmethod
    def get_indexes_info(self):
        pass

    @abstractmethod
    def get_foreign_keys(self):
        pass

    @property
    @abstractmethod
    def db_type(self):
        pass

    @property
    @abstractmethod
    def db_name(self):
        pass


class MySQLConnection(DatabaseConnection):
    """MySQL database connection."""

    def __init__(self, host, user, password, database):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        self.connection = None
        self._db_name = database

    @property
    def db_type(self):
        return 'mysql'

    @property
    def db_name(self):
        return self._db_name

    def connect(self):
        import mysql.connector
        from mysql.connector import Error
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print(f"Connected to MySQL database: {self._db_name}")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
        return False

    def execute(self, query):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def get_tables_info(self):
        query = """
        SELECT
            TABLE_NAME,
            TABLE_TYPE,
            ENGINE,
            TABLE_ROWS,
            DATA_LENGTH,
            TABLE_COMMENT
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_ROWS DESC, TABLE_NAME
        """
        return self.execute(query)

    def get_columns_info(self):
        query = """
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            ORDINAL_POSITION,
            COLUMN_DEFAULT,
            IS_NULLABLE,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            COLUMN_TYPE,
            COLUMN_KEY,
            EXTRA,
            COLUMN_COMMENT
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, ORDINAL_POSITION
        """
        return self.execute(query)

    def get_indexes_info(self):
        query = """
        SELECT
            TABLE_NAME,
            INDEX_NAME,
            NON_UNIQUE,
            SEQ_IN_INDEX,
            COLUMN_NAME,
            INDEX_TYPE
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
        """
        return self.execute(query)

    def get_foreign_keys(self):
        query = """
        SELECT
            tc.CONSTRAINT_NAME,
            tc.TABLE_NAME,
            kcu.COLUMN_NAME,
            kcu.REFERENCED_TABLE_NAME,
            kcu.REFERENCED_COLUMN_NAME
        FROM information_schema.TABLE_CONSTRAINTS tc
        JOIN information_schema.KEY_COLUMN_USAGE kcu
            ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
        WHERE tc.TABLE_SCHEMA = DATABASE()
            AND tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
        ORDER BY tc.TABLE_NAME
        """
        return self.execute(query)


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection."""

    def __init__(self, host, port, user, password, database):
        self.config = {
            'host': host,
            'port': port or 5432,
            'user': user,
            'password': password,
            'dbname': database,
        }
        self.connection = None
        self._db_name = database

    @property
    def db_type(self):
        return 'postgresql'

    @property
    def db_name(self):
        return self._db_name

    def connect(self):
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            print("Error: psycopg2 not installed. Run: pip install psycopg2-binary")
            return False
        try:
            self.connection = psycopg2.connect(**self.config)
            print(f"Connected to PostgreSQL database: {self._db_name}")
            return True
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return False

    def execute(self, query):
        try:
            import psycopg2.extras
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    def close(self):
        if self.connection:
            self.connection.close()

    def get_tables_info(self):
        query = """
        SELECT
            t.table_name as "TABLE_NAME",
            'BASE TABLE' as "TABLE_TYPE",
            'PostgreSQL' as "ENGINE",
            COALESCE(s.n_live_tup, 0) as "TABLE_ROWS",
            pg_total_relation_size(quote_ident(t.table_name)::regclass) as "DATA_LENGTH",
            COALESCE(obj_description((quote_ident(t.table_schema) || '.' || quote_ident(t.table_name))::regclass), '') as "TABLE_COMMENT"
        FROM information_schema.tables t
        LEFT JOIN pg_stat_user_tables s ON t.table_name = s.relname
        WHERE t.table_schema = 'public'
            AND t.table_type = 'BASE TABLE'
        ORDER BY s.n_live_tup DESC NULLS LAST, t.table_name
        """
        return self.execute(query)

    def get_columns_info(self):
        query = """
        SELECT
            c.table_name as "TABLE_NAME",
            c.column_name as "COLUMN_NAME",
            c.ordinal_position as "ORDINAL_POSITION",
            c.column_default as "COLUMN_DEFAULT",
            c.is_nullable as "IS_NULLABLE",
            c.data_type as "DATA_TYPE",
            c.character_maximum_length as "CHARACTER_MAXIMUM_LENGTH",
            c.numeric_precision as "NUMERIC_PRECISION",
            c.numeric_scale as "NUMERIC_SCALE",
            CASE
                WHEN c.character_maximum_length IS NOT NULL
                THEN c.data_type || '(' || c.character_maximum_length || ')'
                ELSE c.data_type
            END as "COLUMN_TYPE",
            CASE
                WHEN pk.column_name IS NOT NULL THEN 'PRI'
                WHEN fk.column_name IS NOT NULL THEN 'MUL'
                ELSE ''
            END as "COLUMN_KEY",
            CASE WHEN c.column_default LIKE 'nextval%' THEN 'auto_increment' ELSE '' END as "EXTRA",
            COALESCE(col_description((quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass, c.ordinal_position), '') as "COLUMN_COMMENT"
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT kcu.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public'
        ) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
        LEFT JOIN (
            SELECT kcu.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
        ) fk ON c.table_name = fk.table_name AND c.column_name = fk.column_name
        WHERE c.table_schema = 'public'
        ORDER BY c.table_name, c.ordinal_position
        """
        return self.execute(query)

    def get_indexes_info(self):
        query = """
        SELECT
            t.relname as "TABLE_NAME",
            i.relname as "INDEX_NAME",
            CASE WHEN ix.indisunique THEN 0 ELSE 1 END as "NON_UNIQUE",
            a.attnum as "SEQ_IN_INDEX",
            a.attname as "COLUMN_NAME",
            am.amname as "INDEX_TYPE"
        FROM pg_class t
        JOIN pg_index ix ON t.oid = ix.indrelid
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_am am ON i.relam = am.oid
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
        WHERE t.relkind = 'r'
            AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        ORDER BY t.relname, i.relname, a.attnum
        """
        return self.execute(query)

    def get_foreign_keys(self):
        query = """
        SELECT
            tc.constraint_name as "CONSTRAINT_NAME",
            tc.table_name as "TABLE_NAME",
            kcu.column_name as "COLUMN_NAME",
            ccu.table_name as "REFERENCED_TABLE_NAME",
            ccu.column_name as "REFERENCED_COLUMN_NAME"
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
        ORDER BY tc.table_name
        """
        return self.execute(query)


class SQLiteConnection(DatabaseConnection):
    """SQLite database connection."""

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.connection = None
        self._db_name = self.filepath.stem

    @property
    def db_type(self):
        return 'sqlite'

    @property
    def db_name(self):
        return self._db_name

    def connect(self):
        import sqlite3
        try:
            if not self.filepath.exists():
                print(f"Error: SQLite file not found: {self.filepath}")
                return False
            self.connection = sqlite3.connect(str(self.filepath))
            self.connection.row_factory = sqlite3.Row
            print(f"Connected to SQLite database: {self.filepath}")
            return True
        except Exception as e:
            print(f"Error connecting to SQLite: {e}")
            return False

    def execute(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            # Convert sqlite3.Row to dict
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    def close(self):
        if self.connection:
            self.connection.close()

    def get_tables_info(self):
        # Get list of tables
        tables = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )

        result = []
        for table in tables:
            table_name = table['name']
            # Get row count
            count_result = self.execute(f"SELECT COUNT(*) as cnt FROM `{table_name}`")
            row_count = count_result[0]['cnt'] if count_result else 0

            result.append({
                'TABLE_NAME': table_name,
                'TABLE_TYPE': 'BASE TABLE',
                'ENGINE': 'SQLite',
                'TABLE_ROWS': row_count,
                'DATA_LENGTH': None,
                'TABLE_COMMENT': ''
            })

        # Sort by row count
        result.sort(key=lambda x: x['TABLE_ROWS'] or 0, reverse=True)
        return result

    def get_columns_info(self):
        tables = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )

        result = []
        for table in tables:
            table_name = table['name']
            columns = self.execute(f"PRAGMA table_info(`{table_name}`)")

            for col in columns:
                # Parse type to extract data type and length
                col_type = col.get('type', 'TEXT') or 'TEXT'
                data_type = col_type.split('(')[0].upper()

                result.append({
                    'TABLE_NAME': table_name,
                    'COLUMN_NAME': col['name'],
                    'ORDINAL_POSITION': col['cid'] + 1,
                    'COLUMN_DEFAULT': col['dflt_value'],
                    'IS_NULLABLE': 'NO' if col['notnull'] else 'YES',
                    'DATA_TYPE': data_type.lower(),
                    'CHARACTER_MAXIMUM_LENGTH': None,
                    'NUMERIC_PRECISION': None,
                    'NUMERIC_SCALE': None,
                    'COLUMN_TYPE': col_type,
                    'COLUMN_KEY': 'PRI' if col['pk'] else '',
                    'EXTRA': 'auto_increment' if col['pk'] and data_type == 'INTEGER' else '',
                    'COLUMN_COMMENT': ''
                })

        return result

    def get_indexes_info(self):
        tables = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )

        result = []
        for table in tables:
            table_name = table['name']
            indexes = self.execute(f"PRAGMA index_list(`{table_name}`)")

            for idx in indexes:
                idx_info = self.execute(f"PRAGMA index_info(`{idx['name']}`)")
                for seq, col_info in enumerate(idx_info):
                    result.append({
                        'TABLE_NAME': table_name,
                        'INDEX_NAME': idx['name'],
                        'NON_UNIQUE': 0 if idx.get('unique') else 1,
                        'SEQ_IN_INDEX': seq + 1,
                        'COLUMN_NAME': col_info['name'],
                        'INDEX_TYPE': 'BTREE'
                    })

        return result

    def get_foreign_keys(self):
        tables = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )

        result = []
        for table in tables:
            table_name = table['name']
            fks = self.execute(f"PRAGMA foreign_key_list(`{table_name}`)")

            for fk in fks:
                result.append({
                    'CONSTRAINT_NAME': f"fk_{table_name}_{fk['from']}",
                    'TABLE_NAME': table_name,
                    'COLUMN_NAME': fk['from'],
                    'REFERENCED_TABLE_NAME': fk['table'],
                    'REFERENCED_COLUMN_NAME': fk['to']
                })

        return result


# =============================================================================
# Schema Extraction Functions
# =============================================================================

def get_table_row_counts(db, tables):
    """Get row counts for tables."""
    counts = {}
    for table in tables:
        try:
            result = db.execute(f"SELECT COUNT(*) as cnt FROM `{table}`")
            if result:
                counts[table] = result[0]['cnt']
        except:
            counts[table] = 'N/A'
    return counts


def detect_enum_columns(db, columns_info, tables_info):
    """Detect columns that contain enum-like values."""
    print("Detecting enum-like columns...")
    enum_values = {}

    tables_with_rows = {t['TABLE_NAME']: t['TABLE_ROWS'] or 0 for t in tables_info}

    table_columns = {}
    for col in columns_info:
        table = col['TABLE_NAME']
        if table not in table_columns:
            table_columns[table] = []
        table_columns[table].append(col)

    for table, cols in table_columns.items():
        if tables_with_rows.get(table, 0) < CONFIG['enum_min_rows']:
            continue

        for col in cols:
            col_name = col['COLUMN_NAME']
            data_type = (col.get('DATA_TYPE') or 'text').lower()

            if not any(t in data_type for t in CONFIG['enum_column_types']):
                continue

            try:
                count_result = db.execute(f"""
                    SELECT COUNT(DISTINCT `{col_name}`) as cnt
                    FROM `{table}`
                    WHERE `{col_name}` IS NOT NULL AND `{col_name}` != ''
                """)
                if not count_result or count_result[0]['cnt'] > CONFIG['enum_max_distinct']:
                    continue

                values_result = db.execute(f"""
                    SELECT `{col_name}` as val, COUNT(*) as cnt
                    FROM `{table}`
                    WHERE `{col_name}` IS NOT NULL AND `{col_name}` != ''
                    GROUP BY `{col_name}`
                    ORDER BY cnt DESC
                    LIMIT {CONFIG['enum_max_distinct']}
                """)

                if values_result:
                    valid_values = [
                        {'value': str(v['val']), 'count': v['cnt']}
                        for v in values_result
                        if len(str(v['val'])) <= CONFIG['enum_max_value_length']
                    ]

                    if valid_values:
                        if table not in enum_values:
                            enum_values[table] = {}
                        enum_values[table][col_name] = valid_values

            except Exception:
                continue

    return enum_values


def detect_json_columns(db, columns_info, tables_info):
    """Detect columns that contain JSON data."""
    print("Detecting JSON columns...")
    json_info = {}

    tables_with_rows = {t['TABLE_NAME']: t['TABLE_ROWS'] or 0 for t in tables_info}

    for col in columns_info:
        table = col['TABLE_NAME']
        col_name = col['COLUMN_NAME']
        data_type = (col.get('DATA_TYPE') or '').lower()

        if tables_with_rows.get(table, 0) == 0:
            continue

        if not any(t in data_type for t in CONFIG['json_column_types']):
            continue

        try:
            # SQLite-compatible query
            sample_query = f"""
                SELECT `{col_name}`
                FROM `{table}`
                WHERE `{col_name}` IS NOT NULL
                  AND `{col_name}` != ''
                  AND (`{col_name}` LIKE '{{%' OR `{col_name}` LIKE '[%')
                LIMIT {CONFIG['json_sample_size']}
            """
            samples = db.execute(sample_query)

            if not samples:
                continue

            all_keys = set()
            nested_keys = {}

            for sample in samples:
                val = sample[col_name]
                if not val:
                    continue
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, dict):
                        all_keys.update(parsed.keys())
                        for key, value in parsed.items():
                            if isinstance(value, dict):
                                if key not in nested_keys:
                                    nested_keys[key] = set()
                                nested_keys[key].update(value.keys())
                except json.JSONDecodeError:
                    continue

            if all_keys:
                if table not in json_info:
                    json_info[table] = {}
                json_info[table][col_name] = {
                    'keys': sorted(list(all_keys)),
                    'nested': {k: sorted(list(v)) for k, v in nested_keys.items()}
                }

        except Exception:
            continue

    return json_info


def detect_date_columns(columns_info):
    """Detect date/time columns."""
    date_columns = {}
    date_types = ['date', 'datetime', 'timestamp', 'time', 'year']

    for col in columns_info:
        data_type = (col.get('DATA_TYPE') or '').lower()
        if data_type in date_types:
            table = col['TABLE_NAME']
            if table not in date_columns:
                date_columns[table] = []
            date_columns[table].append({
                'column': col['COLUMN_NAME'],
                'type': data_type
            })

    return date_columns


def detect_primary_keys(columns_info):
    """Detect primary key columns."""
    pk_columns = {}

    for col in columns_info:
        if col.get('COLUMN_KEY') == 'PRI':
            table = col['TABLE_NAME']
            if table not in pk_columns:
                pk_columns[table] = []
            pk_columns[table].append(col['COLUMN_NAME'])

    return pk_columns


def extract_all_data(db):
    """Extract all schema data from the database."""
    print("Extracting tables info...")
    tables = db.get_tables_info()
    table_names = [t['TABLE_NAME'] for t in tables]

    print("Extracting columns info...")
    columns = db.get_columns_info()

    print("Extracting indexes info...")
    indexes = db.get_indexes_info()

    print("Extracting foreign keys...")
    foreign_keys = db.get_foreign_keys()

    print("Getting row counts...")
    top_tables = [t['TABLE_NAME'] for t in sorted(tables, key=lambda x: x['TABLE_ROWS'] or 0, reverse=True)[:20]]
    row_counts = get_table_row_counts(db, top_tables)

    enum_values = detect_enum_columns(db, columns, tables)
    json_info = detect_json_columns(db, columns, tables)
    date_columns = detect_date_columns(columns)
    primary_keys = detect_primary_keys(columns)

    return {
        'extracted_at': datetime.now().isoformat(),
        'database': db.db_name,
        'db_type': db.db_type,
        'tables': tables,
        'columns': columns,
        'indexes': indexes,
        'foreign_keys': foreign_keys,
        'row_counts': row_counts,
        'enum_values': enum_values,
        'json_fields': json_info,
        'date_columns': date_columns,
        'primary_keys': primary_keys
    }


# =============================================================================
# Documentation Generation
# =============================================================================

def generate_markdown_documentation(data):
    """Generate human-readable documentation."""
    md = []
    md.append(f"# Database Documentation: {data['database']}")
    md.append(f"\n*Generated: {data['extracted_at']}*")
    md.append(f"\n*Database Type: {data['db_type'].upper()}*")

    md.append("\n## Table of Contents")
    md.append("1. [Overview](#overview)")
    md.append("2. [Tables](#tables)")
    md.append("3. [Table Details](#table-details)")
    md.append("4. [Relationships](#relationships)")
    md.append("5. [Enum Values](#enum-values)")
    md.append("6. [JSON Fields](#json-fields)")

    md.append("\n## Overview")
    md.append(f"\n- **Database:** {data['database']}")
    md.append(f"- **Type:** {data['db_type'].upper()}")
    md.append(f"- **Total Tables:** {len(data['tables'])}")

    md.append("\n### Row Counts (Top Tables)")
    for table, count in sorted(data['row_counts'].items(), key=lambda x: x[1] if isinstance(x[1], int) else 0, reverse=True):
        md.append(f"- **{table}**: {count:,} rows" if isinstance(count, int) else f"- **{table}**: {count}")

    md.append("\n## Tables")
    md.append("\n| Table Name | Engine | Est. Rows | Description |")
    md.append("|------------|--------|-----------|-------------|")

    for table in data['tables']:
        rows = f"{table['TABLE_ROWS']:,}" if table['TABLE_ROWS'] else 'N/A'
        comment = table.get('TABLE_COMMENT') or '-'
        md.append(f"| {table['TABLE_NAME']} | {table['ENGINE']} | {rows} | {comment} |")

    md.append("\n## Table Details")

    tables_columns = {}
    for col in data['columns']:
        table = col['TABLE_NAME']
        if table not in tables_columns:
            tables_columns[table] = []
        tables_columns[table].append(col)

    sorted_tables = sorted(data['tables'], key=lambda x: x['TABLE_ROWS'] if x['TABLE_ROWS'] else 0, reverse=True)

    for table_info in sorted_tables[:30]:
        table_name = table_info['TABLE_NAME']
        if table_name in tables_columns:
            md.append(f"\n### {table_name}")
            md.append("\n| Column | Type | Key | Nullable |")
            md.append("|--------|------|-----|----------|")

            for col in tables_columns[table_name]:
                key = col.get('COLUMN_KEY') or '-'
                nullable = col.get('IS_NULLABLE', 'YES')
                md.append(f"| {col['COLUMN_NAME']} | {col['COLUMN_TYPE']} | {key} | {nullable} |")

    md.append("\n## Relationships")
    if data['foreign_keys']:
        md.append("\n| Table | Column | References | Referenced Column |")
        md.append("|-------|--------|------------|-------------------|")
        for fk in data['foreign_keys']:
            md.append(f"| {fk['TABLE_NAME']} | {fk['COLUMN_NAME']} | {fk['REFERENCED_TABLE_NAME']} | {fk['REFERENCED_COLUMN_NAME']} |")
    else:
        md.append("\nNo foreign key constraints found.")

    md.append("\n## Enum Values")
    if data['enum_values']:
        for table, columns in data['enum_values'].items():
            md.append(f"\n### {table}")
            for col, values in columns.items():
                md.append(f"\n**{col}:**")
                for v in values[:20]:
                    md.append(f"- `{v['value']}` ({v['count']:,} rows)")
    else:
        md.append("\nNo enum-like columns detected.")

    md.append("\n## JSON Fields")
    if data['json_fields']:
        for table, columns in data['json_fields'].items():
            md.append(f"\n### {table}")
            for col, info in columns.items():
                md.append(f"\n**{col}:**")
                md.append("\nTop-level keys:")
                for key in info['keys'][:30]:
                    md.append(f"- `{key}`")
    else:
        md.append("\nNo JSON fields detected.")

    return '\n'.join(md)


def generate_text_to_sql_context(data):
    """Generate optimized context for LLM text-to-sql tasks."""
    ctx = []
    db_type = data['db_type'].upper()

    ctx.append(f"# Database Context for Text-to-SQL: {data['database']}")
    ctx.append(f"\n*Database: {data['database']} ({db_type})*")

    ctx.append("\n## Database Overview")
    ctx.append(f"This {db_type} database contains {len(data['tables'])} tables.")

    ctx.append("\n## Main Tables (by size)")
    sorted_counts = sorted(data['row_counts'].items(), key=lambda x: x[1] if isinstance(x[1], int) else 0, reverse=True)

    for table, count in sorted_counts[:10]:
        if isinstance(count, int):
            ctx.append(f"- `{table}`: ~{count:,} rows")

    tables_columns = {}
    for col in data['columns']:
        table = col['TABLE_NAME']
        if table not in tables_columns:
            tables_columns[table] = []
        tables_columns[table].append(col)

    ctx.append("\n## Table Schemas")

    sorted_tables = sorted(data['tables'], key=lambda x: x['TABLE_ROWS'] if x['TABLE_ROWS'] else 0, reverse=True)

    for table_info in sorted_tables[:15]:
        table_name = table_info['TABLE_NAME']
        if table_name not in tables_columns:
            continue

        ctx.append(f"\n### {table_name}")

        if table_name in data['primary_keys']:
            ctx.append(f"**Primary Key:** {', '.join(data['primary_keys'][table_name])}")

        ctx.append("\n**Columns:**")
        for col in tables_columns[table_name]:
            key_info = " (PK)" if col.get('COLUMN_KEY') == 'PRI' else ""
            key_info += " (FK)" if col.get('COLUMN_KEY') == 'MUL' else ""
            ctx.append(f"- `{col['COLUMN_NAME']}` {col['COLUMN_TYPE']}{key_info}")

    if data['enum_values']:
        ctx.append("\n## Important Enum Values")
        for table, columns in data['enum_values'].items():
            for col, values in columns.items():
                if len(values) <= 15:
                    ctx.append(f"\n**{table}.{col}:**")
                    vals = [f"`{v['value']}`" for v in values]
                    ctx.append(f"Values: {', '.join(vals)}")

    if data['json_fields']:
        ctx.append("\n## JSON Field Access")
        if data['db_type'] == 'mysql':
            ctx.append("\nUse MySQL JSON functions:")
            ctx.append("```sql")
            ctx.append("JSON_UNQUOTE(JSON_EXTRACT(column_name, '$.key'))")
            ctx.append("```")
        else:
            ctx.append("\nSQLite has limited JSON support. Use json_extract():")
            ctx.append("```sql")
            ctx.append("json_extract(column_name, '$.key')")
            ctx.append("```")

    if data['date_columns']:
        ctx.append("\n## Date/Time Columns")
        for table, cols in data['date_columns'].items():
            col_list = [f"`{c['column']}` ({c['type']})" for c in cols]
            ctx.append(f"- **{table}**: {', '.join(col_list)}")

        ctx.append("\n### Date Filtering Patterns")
        if data['db_type'] == 'mysql':
            ctx.append("```sql")
            ctx.append("-- Specific date range")
            ctx.append("WHERE date_column >= '2024-01-01' AND date_column < '2024-02-01'")
            ctx.append("```")
        else:
            ctx.append("```sql")
            ctx.append("-- Specific date range (SQLite)")
            ctx.append("WHERE date_column >= '2024-01-01' AND date_column < '2024-02-01'")
            ctx.append("-- Or use date() function")
            ctx.append("WHERE date(date_column) BETWEEN '2024-01-01' AND '2024-01-31'")
            ctx.append("```")

    if data['foreign_keys']:
        ctx.append("\n## Table Relationships")
        for fk in data['foreign_keys']:
            ctx.append(f"- `{fk['TABLE_NAME']}.{fk['COLUMN_NAME']}` -> `{fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}`")

    ctx.append("\n## Common Query Patterns")
    ctx.append("```sql")
    ctx.append("-- Count records")
    ctx.append("SELECT COUNT(*) FROM table_name;")
    ctx.append("")
    ctx.append("-- Group by with count")
    ctx.append("SELECT column, COUNT(*) as count")
    ctx.append("FROM table_name")
    ctx.append("GROUP BY column")
    ctx.append("ORDER BY count DESC;")
    ctx.append("")
    ctx.append("-- JOIN example")
    ctx.append("SELECT t1.*, t2.column")
    ctx.append("FROM table1 t1")
    ctx.append("JOIN table2 t2 ON t1.id = t2.foreign_id;")
    ctx.append("```")

    return '\n'.join(ctx)


def generate_cursor_instructions(data, connection_config=None):
    """Generate instructions for Cursor to create SQL examples."""
    md = []
    db_type = data['db_type'].upper()
    run_cmd = connection_config.get('run_command', 'python query_runner.py') if connection_config else 'python query_runner.py'

    md.append(f"# Cursor Instructions for {data['database']} ({db_type})")
    md.append(f"""
## ВАЖНО: Как выполнять запросы

**База данных:** {data['database']}
**Тип:** {db_type}

### Команда для выполнения SQL-запросов:
```bash
{run_cmd} -f output/queries/QUERY_NAME.sql -o RESULT_NAME.csv
```

### Команда для быстрого запроса:
```bash
{run_cmd} "SELECT * FROM table_name LIMIT 10"
```

---

## Workflow: Когда пользователь просит данные

1. **Создай SQL-запрос** на основе `output/text_to_sql_context.md`
2. **Сохрани запрос** в файл `output/queries/descriptive_name.sql`
3. **Выполни команду:**
   ```bash
   {run_cmd} -f output/queries/descriptive_name.sql -o result.csv
   ```
4. **Сообщи пользователю:** "Данные сохранены в output/reports/result.csv"

### Пример:
```
Пользователь: "Покажи все заказы за январь 2024"

1. Создаю файл output/queries/orders_jan_2024.sql:
   SELECT * FROM orders
   WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01';

2. Выполняю: {run_cmd} -f output/queries/orders_jan_2024.sql -o orders_jan_2024.csv

3. Отвечаю: "Данные сохранены в output/reports/orders_jan_2024.csv"
```

---

## Генерация примеров SQL

Для создания файла `output/text_to_sql_examples.md` с примерами запросов:

1. **Изучи схему** в `output/text_to_sql_context.md`
2. **Создай примеры** для категорий:
   - Подсчёты и статистика
   - Фильтрация по дате, категории
   - Агрегации (SUM, AVG, COUNT с GROUP BY)
   - Анализ по времени
   - Top-N запросы
   - JOINы между таблицами

3. **Формат примера:**
   ```
   ### Q: [Вопрос на русском]
   ```sql
   [SQL запрос]
   ```
   ```

---
""")

    md.append("## Schema-Specific Guidance\n")

    md.append("### Detected Tables (by importance)")
    sorted_tables = sorted(data['tables'], key=lambda x: x['TABLE_ROWS'] if x['TABLE_ROWS'] else 0, reverse=True)
    for t in sorted_tables[:10]:
        rows = t['TABLE_ROWS'] or 0
        md.append(f"- `{t['TABLE_NAME']}` (~{rows:,} rows)")

    if data['enum_values']:
        md.append("\n### Detected Categorical Columns (for filtering)")
        for table, columns in data['enum_values'].items():
            for col, values in columns.items():
                vals = [v['value'] for v in values[:5]]
                md.append(f"- `{table}.{col}`: {', '.join(vals)}{'...' if len(values) > 5 else ''}")

    if data['foreign_keys']:
        md.append("\n### Table Relationships (for JOINs)")
        for fk in data['foreign_keys'][:15]:
            md.append(f"- `{fk['TABLE_NAME']}.{fk['COLUMN_NAME']}` -> `{fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}`")

    if data['date_columns']:
        md.append("\n### Date Columns (for time analysis)")
        for table, cols in data['date_columns'].items():
            for c in cols:
                md.append(f"- `{table}.{c['column']}` ({c['type']})")

    return '\n'.join(md)


# =============================================================================
# Main
# =============================================================================

def get_db_config(database_override=None):
    """Get database configuration from environment."""
    db_name = database_override or os.getenv('DB_NAME') or os.getenv('DB_DATABASE') or os.getenv('DATABASE')
    db_type = (os.getenv('DB_TYPE') or 'mysql').lower()
    return {
        'type': db_type,
        'host': os.getenv('DB_IP') or os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'user': os.getenv('DB_USER') or os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD') or os.getenv('DB_PASS'),
        'database': db_name
    }


def list_databases():
    """List available databases."""
    config = get_db_config()
    if not config.get('host') or not config.get('user'):
        print("Error: Database credentials not found in .env")
        print("Expected: DB_TYPE, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD")
        return

    db_type = config['type']

    if db_type == 'postgresql':
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'] or 5432,
                user=config['user'],
                password=config['password'],
                dbname='postgres'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
            databases = [row[0] for row in cursor.fetchall()]
            print(f"\nAvailable PostgreSQL databases:")
            for db in databases:
                print(f"  - {db}")
            conn.close()
        except Exception as e:
            print(f"Error: {e}")
    else:  # mysql/mariadb
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=config['host'],
                port=config['port'] or 3306,
                user=config['user'],
                password=config['password']
            )
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            skip = CONFIG['skip_tables_patterns']
            databases = [row[0] for row in cursor.fetchall() if row[0].lower() not in skip]
            print(f"\nAvailable MySQL/MariaDB databases:")
            for db in databases:
                print(f"  - {db}")
            conn.close()
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Universal Database Schema Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # SQLite
  python db_extractor.py --sqlite path/to/database.sqlite

  # PostgreSQL/MySQL (uses .env with DB_TYPE)
  python db_extractor.py --database mydb
  python db_extractor.py --list-databases
        """
    )

    # Connection type
    parser.add_argument('--sqlite', '-s', metavar='PATH',
                        help='Path to SQLite database file')
    parser.add_argument('--database', '-d', metavar='NAME',
                        help='Database name (PostgreSQL/MySQL)')
    parser.add_argument('--list-databases', '-l', action='store_true',
                        help='List available databases')

    args = parser.parse_args()

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # List databases
    if args.list_databases:
        list_databases()
        return

    # Determine connection type
    if args.sqlite:
        db = SQLiteConnection(args.sqlite)
    else:
        config = get_db_config(args.database)

        if not config.get('host') or not config.get('user'):
            print("Error: Database credentials not found in .env file")
            print("Expected: DB_TYPE, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD")
            print("\nAlternatively, use SQLite:")
            print("  python db_extractor.py --sqlite path/to/database.sqlite")
            sys.exit(1)

        if not config.get('database'):
            print("Error: No database specified.")
            print("Use: python db_extractor.py --database YOUR_DB_NAME")
            print("Or:  python db_extractor.py --list-databases")
            sys.exit(1)

        db_type = config['type']
        if db_type == 'postgresql':
            db = PostgreSQLConnection(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database']
            )
        else:  # mysql/mariadb
            db = MySQLConnection(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database=config['database']
            )

    # Connect
    if not db.connect():
        sys.exit(1)

    try:
        print(f"\n=== Extracting {db.db_type.upper()} Database Schema ===\n")
        data = extract_all_data(db)

        # Save JSON
        json_path = OUTPUT_DIR / 'schema_info.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        print(f"\nSaved JSON schema to: {json_path}")

        # Save connection config for Cursor
        connection_config = {
            'db_type': db.db_type,
            'db_name': db.db_name,
        }
        if db.db_type == 'sqlite':
            # Save relative path from project directory
            sqlite_path = Path(args.sqlite).absolute()
            project_dir = Path(__file__).parent.absolute()
            try:
                connection_config['sqlite_path'] = str(sqlite_path.relative_to(project_dir))
            except ValueError:
                connection_config['sqlite_path'] = str(sqlite_path)
            connection_config['run_command'] = f"python query_runner.py --sqlite {connection_config['sqlite_path']}"
        else:
            connection_config['run_command'] = "python query_runner.py"

        conn_path = OUTPUT_DIR / 'connection.json'
        with open(conn_path, 'w', encoding='utf-8') as f:
            json.dump(connection_config, f, indent=2, ensure_ascii=False)
        print(f"Saved connection config to: {conn_path}")

        # Save documentation
        md_doc = generate_markdown_documentation(data)
        md_path = OUTPUT_DIR / 'database_documentation.md'
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_doc)
        print(f"Saved documentation to: {md_path}")

        # Save text-to-sql context
        ctx_doc = generate_text_to_sql_context(data)
        ctx_path = OUTPUT_DIR / 'text_to_sql_context.md'
        with open(ctx_path, 'w', encoding='utf-8') as f:
            f.write(ctx_doc)
        print(f"Saved text-to-sql context to: {ctx_path}")

        # Save cursor instructions with connection info
        cursor_doc = generate_cursor_instructions(data, connection_config)
        cursor_path = OUTPUT_DIR / 'cursor_instructions.md'
        with open(cursor_path, 'w', encoding='utf-8') as f:
            f.write(cursor_doc)
        print(f"Saved cursor instructions to: {cursor_path}")

        print("\n=== Extraction Complete ===")
        print(f"\nNext steps:")
        print(f"1. Review generated documentation in output/")
        print(f"2. Ask Cursor to generate SQL examples based on output/cursor_instructions.md")

    finally:
        db.close()
        print("Database connection closed.")


if __name__ == '__main__':
    main()
