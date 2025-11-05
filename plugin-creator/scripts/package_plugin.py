#!/usr/bin/env python3
"""
Plugin Packaging Script

Packages plugin into distributable archive with validation.
"""

import argparse
import os
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Optional
import tempfile


def run_validation(plugin_path: Path) -> bool:
    """
    Run validation script

    Args:
        plugin_path: Path to plugin

    Returns:
        True if validation passes
    """
    script_dir = Path(__file__).parent
    validate_script = script_dir / "validate_plugin.py"

    if not validate_script.exists():
        print("Warning: validate_plugin.py not found, skipping validation")
        return True

    print("Running validation...")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, str(validate_script), str(plugin_path)],
            capture_output=False,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running validation: {e}")
        return False


def should_exclude(path: Path, plugin_root: Path) -> bool:
    """
    Check if path should be excluded from package

    Args:
        path: Path to check
        plugin_root: Root of plugin directory

    Returns:
        True if should be excluded
    """
    # Patterns to exclude
    exclude_patterns = [
        # Version control
        ".git",
        ".gitignore",
        # Dependencies
        "node_modules",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        # Build artifacts
        "dist",
        "build",
        ".tsbuildinfo",
        # IDE
        ".vscode",
        ".idea",
        "*.swp",
        # OS
        ".DS_Store",
        "Thumbs.db",
        # Temporary
        "*.tmp",
        "*.log",
    ]

    # Get relative path
    try:
        rel_path = path.relative_to(plugin_root)
    except ValueError:
        return False

    # Check each part of path against patterns
    for part in rel_path.parts:
        for pattern in exclude_patterns:
            if pattern.startswith("*"):
                # Wildcard pattern
                if part.endswith(pattern[1:]):
                    return True
            else:
                # Exact match
                if part == pattern:
                    return True

    return False


def create_package(
    plugin_path: Path,
    output_dir: Optional[Path] = None,
    skip_validation: bool = False,
) -> Optional[Path]:
    """
    Create plugin package

    Args:
        plugin_path: Path to plugin directory
        output_dir: Output directory for package (default: current directory)
        skip_validation: Skip validation step

    Returns:
        Path to created package, or None if failed
    """
    if not plugin_path.exists():
        print(f"Error: Plugin path does not exist: {plugin_path}", file=sys.stderr)
        return None

    if not plugin_path.is_dir():
        print(f"Error: Plugin path is not a directory: {plugin_path}", file=sys.stderr)
        return None

    # Run validation unless skipped
    if not skip_validation:
        if not run_validation(plugin_path):
            print("\nValidation failed. Use --skip-validation to package anyway.")
            return None
    else:
        print("Skipping validation (--skip-validation specified)")

    # Determine package name
    plugin_name = plugin_path.name
    package_name = f"{plugin_name}.zip"

    # Determine output path
    if output_dir:
        output_path = output_dir / package_name
    else:
        output_path = Path.cwd() / package_name

    if output_path.exists():
        print(f"Warning: Package already exists: {output_path}")
        response = input("Overwrite? (y/N): ")
        if response.lower() != "y":
            print("Packaging cancelled")
            return None
        output_path.unlink()

    # Create temporary directory for packaging
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / plugin_name

        print(f"\nPreparing package: {plugin_name}")
        print("=" * 60)

        # Copy plugin files, excluding unwanted files
        print("Copying files...")
        copied_files = []

        for item in plugin_path.rglob("*"):
            if should_exclude(item, plugin_path):
                continue

            if item.is_file():
                # Calculate relative path
                rel_path = item.relative_to(plugin_path)
                dest_path = temp_path / rel_path

                # Create parent directories
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(item, dest_path)
                copied_files.append(str(rel_path))

        print(f"Copied {len(copied_files)} files")

        # Build MCP server if needed
        if (temp_path / "package.json").exists():
            print("\nTypeScript MCP server detected")
            print("Note: Include build instructions in README for users")
            print("Or pre-build before packaging:")
            print("  cd plugin && npm run build && cd ..")

        if (temp_path / "pyproject.toml").exists():
            print("\nPython MCP server detected")
            print("Note: Include installation instructions in README for users")
            print("Package will be installed with: pip install .")

        # Create package
        print(f"\nCreating package: {output_path}")

        try:
            # Create zip archive
            shutil.make_archive(
                str(output_path.with_suffix("")),  # Base name without .zip
                "zip",  # Format
                temp_dir,  # Root directory
                plugin_name,  # Base directory in archive
            )

            print(f"\n✓ Package created successfully: {output_path}")

            # Show package info
            package_size = output_path.stat().st_size
            size_mb = package_size / (1024 * 1024)
            print(f"  Size: {size_mb:.2f} MB")
            print(f"  Files: {len(copied_files)}")

            return output_path

        except Exception as e:
            print(f"Error creating package: {e}", file=sys.stderr)
            return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Package Claude Code plugin for distribution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Package plugin with validation
  python package_plugin.py my-plugin

  # Package to specific directory
  python package_plugin.py my-plugin --output dist/

  # Package without validation
  python package_plugin.py my-plugin --skip-validation

Packaging Process:
  1. Validates plugin (unless --skip-validation)
  2. Copies plugin files (excludes node_modules, __pycache__, etc.)
  3. Creates ZIP archive
  4. Reports package information
""",
    )

    parser.add_argument(
        "plugin_path",
        help="Path to plugin directory to package",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output directory for package (default: current directory)",
    )

    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation before packaging",
    )

    args = parser.parse_args()

    plugin_path = Path(args.plugin_path)
    output_dir = Path(args.output) if args.output else None

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    result = create_package(plugin_path, output_dir, args.skip_validation)

    if result:
        print("\n" + "=" * 60)
        print("DISTRIBUTION")
        print("=" * 60)
        print("""
Next steps:
  1. Test installation from package
  2. Write clear installation instructions
  3. Consider publishing to:
     - npm (for TypeScript MCP servers)
     - PyPI (for Python MCP servers)
     - GitHub releases
     - Claude Code plugin marketplace (when available)

Package contents:
  - All plugin files
  - Documentation (README.md, etc.)
  - Source code
  - Configuration files

Users will need to:
  1. Extract the package
  2. Install dependencies (if applicable)
  3. Configure Claude Code
  4. Install components (skill, commands)
""")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
