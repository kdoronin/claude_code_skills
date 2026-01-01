#!/usr/bin/env python3
"""
Text-to-SQL Project Initializer
================================
Sets up project structure for text-to-sql workflow.

Usage:
    python init_project.py [--target /path/to/project]
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_DIR / 'assets'


def init_project(target_dir: Path):
    """Initialize text-to-sql project in target directory."""
    target_dir = target_dir.resolve()

    print(f"Initializing text-to-sql project in: {target_dir}")

    # Create directory structure
    dirs = [
        'database',
        'output',
        'output/queries',
        'output/reports',
    ]

    for d in dirs:
        dir_path = target_dir / d
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {d}/")

    # Create .gitkeep files
    for d in ['output/queries', 'output/reports']:
        gitkeep = target_dir / d / '.gitkeep'
        gitkeep.touch()

    # Copy scripts
    scripts = [
        'db_extractor.py',
        'query_runner.py',
        'list_databases.py',
        'sql_helper.py',
    ]

    for script in scripts:
        src = SCRIPT_DIR / script
        dst = target_dir / script
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  Copied: {script}")
        else:
            print(f"  Warning: {script} not found in skill scripts/")

    # Copy assets
    assets = [
        ('example.env', 'example.env'),
        ('requirements.txt', 'requirements.txt'),
        ('.gitignore', '.gitignore'),
    ]

    for src_name, dst_name in assets:
        src = ASSETS_DIR / src_name
        dst = target_dir / dst_name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            print(f"  Copied: {dst_name}")

    # Create database README
    db_readme = target_dir / 'database' / 'README.md'
    if not db_readme.exists():
        db_readme.write_text("""# Databases

Place your SQLite database files (.sqlite, .db) in this folder.

## Example

```
database/
├── README.md
├── sales.sqlite
└── users.db
```

## Database Descriptions

Add descriptions for each database to help with database selection:

### sales.sqlite
**Description:** Sales and orders data
**Contains:** orders, products, customers
**Keywords:** sales, revenue, orders

### users.db
**Description:** User management data
**Contains:** users, roles, permissions
**Keywords:** users, authentication, access
""")
        print("  Created: database/README.md")

    print("\n" + "="*50)
    print("Project initialized successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Add your database:")
    print("   - SQLite: Copy .sqlite file to database/")
    print("   - MySQL: Copy example.env to .env and edit credentials")
    print("3. Extract schema:")
    print("   - SQLite: python db_extractor.py --sqlite database/YOUR_DB.sqlite")
    print("   - MySQL: python db_extractor.py --database YOUR_DB_NAME")
    print("4. Start querying! See output/text_to_sql_context.md for schema.")


def main():
    parser = argparse.ArgumentParser(
        description='Initialize text-to-sql project structure'
    )
    parser.add_argument(
        '--target', '-t',
        type=Path,
        default=Path.cwd(),
        help='Target directory (default: current directory)'
    )

    args = parser.parse_args()
    init_project(args.target)


if __name__ == '__main__':
    main()
