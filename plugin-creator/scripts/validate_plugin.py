#!/usr/bin/env python3
"""
Plugin Validation Script

Validates plugin structure, configuration, and documentation.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class ValidationError:
    """Validation error information"""

    def __init__(self, severity: str, message: str, file: Optional[str] = None):
        self.severity = severity  # 'error', 'warning', 'info'
        self.message = message
        self.file = file

    def __str__(self):
        prefix = {
            "error": "❌ ERROR",
            "warning": "⚠️  WARNING",
            "info": "ℹ️  INFO",
        }[self.severity]

        if self.file:
            return f"{prefix} [{self.file}]: {self.message}"
        return f"{prefix}: {self.message}"


class PluginValidator:
    """Plugin validation logic"""

    def __init__(self, plugin_path: Path):
        self.plugin_path = plugin_path
        self.errors: List[ValidationError] = []

    def add_error(self, severity: str, message: str, file: Optional[str] = None):
        """Add validation error"""
        self.errors.append(ValidationError(severity, message, file))

    def validate(self) -> bool:
        """
        Run all validations

        Returns:
            True if validation passes (no errors), False otherwise
        """
        if not self.plugin_path.exists():
            self.add_error("error", f"Plugin path does not exist: {self.plugin_path}")
            return False

        if not self.plugin_path.is_dir():
            self.add_error("error", f"Plugin path is not a directory: {self.plugin_path}")
            return False

        # Detect plugin type and validate accordingly
        has_mcp = self._has_mcp_server()
        has_skill = self._has_skill()
        has_commands = self._has_commands()

        if not (has_mcp or has_skill or has_commands):
            self.add_error(
                "error",
                "No plugin components found (MCP server, skill, or commands)",
            )
            return False

        # Validate each component
        if has_mcp:
            self._validate_mcp_server()
        if has_skill:
            self._validate_skill()
        if has_commands:
            self._validate_commands()

        # Validate documentation
        self._validate_documentation()

        # Return True if no errors (warnings are ok)
        return not any(e.severity == "error" for e in self.errors)

    def _has_mcp_server(self) -> bool:
        """Check if plugin has MCP server component"""
        mcp_indicators = [
            self.plugin_path / "package.json",
            self.plugin_path / "pyproject.toml",
            self.plugin_path / "src" / "index.ts",
            self.plugin_path / "app" / "main.py",
            self.plugin_path / "mcp-server",
        ]
        return any(p.exists() for p in mcp_indicators)

    def _has_skill(self) -> bool:
        """Check if plugin has skill component"""
        skill_indicators = [
            self.plugin_path / "SKILL.md",
            self.plugin_path / "skill" / "SKILL.md",
        ]
        return any(p.exists() for p in skill_indicators)

    def _has_commands(self) -> bool:
        """Check if plugin has command components"""
        commands_indicators = [
            self.plugin_path / "commands",
        ]
        if any(p.exists() for p in commands_indicators):
            return True

        # Check for .md files that might be commands
        md_files = list(self.plugin_path.glob("*.md"))
        return len(md_files) > 1  # More than just README

    def _validate_mcp_server(self):
        """Validate MCP server component"""
        # Check for TypeScript MCP server
        if (self.plugin_path / "package.json").exists():
            self._validate_typescript_mcp()

        # Check for Python MCP server
        if (self.plugin_path / "pyproject.toml").exists():
            self._validate_python_mcp()

    def _validate_typescript_mcp(self):
        """Validate TypeScript MCP server"""
        package_json = self.plugin_path / "package.json"

        try:
            with open(package_json) as f:
                pkg = json.load(f)

            # Check required fields
            if "name" not in pkg:
                self.add_error("error", "Missing 'name' in package.json", "package.json")

            if "version" not in pkg:
                self.add_error(
                    "warning", "Missing 'version' in package.json", "package.json"
                )

            # Check for MCP SDK dependency
            deps = pkg.get("dependencies", {})
            if "@modelcontextprotocol/sdk" not in deps:
                self.add_error(
                    "error",
                    "Missing @modelcontextprotocol/sdk dependency",
                    "package.json",
                )

            # Check for bin entry
            if "bin" not in pkg:
                self.add_error(
                    "warning",
                    "No bin entry in package.json (won't be installable globally)",
                    "package.json",
                )

        except json.JSONDecodeError:
            self.add_error("error", "Invalid JSON format", "package.json")
        except Exception as e:
            self.add_error("error", f"Error reading package.json: {e}", "package.json")

        # Check for source files
        src_dir = self.plugin_path / "src"
        if not src_dir.exists():
            self.add_error("error", "Missing src/ directory")
        elif not (src_dir / "index.ts").exists():
            self.add_error("warning", "Missing src/index.ts entry point")

        # Check for tsconfig
        if not (self.plugin_path / "tsconfig.json").exists():
            self.add_error("warning", "Missing tsconfig.json")

    def _validate_python_mcp(self):
        """Validate Python MCP server"""
        pyproject = self.plugin_path / "pyproject.toml"

        if not pyproject.exists():
            return

        try:
            content = pyproject.read_text()

            # Basic TOML validation (not comprehensive)
            if "[project]" not in content:
                self.add_error("error", "Missing [project] section", "pyproject.toml")

            if "mcp" not in content:
                self.add_error(
                    "warning",
                    "MCP dependency not found in pyproject.toml",
                    "pyproject.toml",
                )

        except Exception as e:
            self.add_error("error", f"Error reading pyproject.toml: {e}", "pyproject.toml")

        # Check for app directory
        app_dir = self.plugin_path / "app"
        if not app_dir.exists():
            self.add_error("error", "Missing app/ directory")
        elif not (app_dir / "main.py").exists():
            self.add_error("warning", "Missing app/main.py entry point")

    def _validate_skill(self):
        """Validate skill component"""
        # Find SKILL.md
        skill_md_paths = [
            self.plugin_path / "SKILL.md",
            self.plugin_path / "skill" / "SKILL.md",
        ]

        skill_md = None
        for path in skill_md_paths:
            if path.exists():
                skill_md = path
                break

        if not skill_md:
            self.add_error("error", "SKILL.md not found")
            return

        try:
            content = skill_md.read_text()

            # Check for YAML frontmatter
            if not content.startswith("---"):
                self.add_error("error", "Missing YAML frontmatter", str(skill_md))
                return

            # Extract frontmatter
            parts = content.split("---", 2)
            if len(parts) < 3:
                self.add_error("error", "Invalid YAML frontmatter format", str(skill_md))
                return

            frontmatter = parts[1]
            body = parts[2]

            # Check for required fields
            if "name:" not in frontmatter:
                self.add_error("error", "Missing 'name' in frontmatter", str(skill_md))

            if "description:" not in frontmatter:
                self.add_error("error", "Missing 'description' in frontmatter", str(skill_md))

            # Extract name and description
            name_match = re.search(r"name:\s*(.+)", frontmatter)
            desc_match = re.search(r"description:\s*(.+)", frontmatter)

            if name_match:
                name = name_match.group(1).strip()
                # Check naming convention
                if not re.match(r"^[a-z0-9-]+$", name):
                    self.add_error(
                        "warning",
                        f"Name should be lowercase-with-dashes: {name}",
                        str(skill_md),
                    )

            if desc_match:
                desc = desc_match.group(1).strip()
                # Check description quality
                if len(desc) < 20:
                    self.add_error(
                        "warning",
                        "Description is too short (should be 1-3 sentences)",
                        str(skill_md),
                    )

                # Check for second person (should use third person)
                if re.search(r"\byou\b|\byour\b", desc.lower()):
                    self.add_error(
                        "warning",
                        "Description uses second person (prefer third person)",
                        str(skill_md),
                    )

            # Check body has content
            if len(body.strip()) < 100:
                self.add_error(
                    "warning",
                    "Skill body is very short (add more content)",
                    str(skill_md),
                )

            # Check for recommended sections
            recommended_sections = [
                ("## Purpose", "Purpose section"),
                ("## When to Use", "When to Use section"),
            ]

            for pattern, name in recommended_sections:
                if pattern not in body:
                    self.add_error("info", f"Missing recommended {name}", str(skill_md))

        except Exception as e:
            self.add_error("error", f"Error reading SKILL.md: {e}", str(skill_md))

    def _validate_commands(self):
        """Validate slash commands"""
        commands_dir = self.plugin_path / "commands"

        if commands_dir.exists():
            command_files = list(commands_dir.glob("*.md"))
        else:
            # Check for .md files in root (excluding README)
            command_files = [
                f for f in self.plugin_path.glob("*.md") if f.name.lower() != "readme.md"
            ]

        if not command_files:
            self.add_error("info", "No command files found")
            return

        for cmd_file in command_files:
            try:
                content = cmd_file.read_text()

                # Check for required sections
                if "## Prompt" not in content:
                    self.add_error(
                        "error", "Missing ## Prompt section", str(cmd_file.name)
                    )

                # Check command has content
                if len(content.strip()) < 50:
                    self.add_error(
                        "warning",
                        "Command file is very short",
                        str(cmd_file.name),
                    )

            except Exception as e:
                self.add_error("error", f"Error reading command file: {e}", str(cmd_file.name))

    def _validate_documentation(self):
        """Validate documentation"""
        readme = self.plugin_path / "README.md"

        if not readme.exists():
            self.add_error("warning", "Missing README.md")
            return

        try:
            content = readme.read_text()

            # Check README has reasonable content
            if len(content.strip()) < 100:
                self.add_error("warning", "README.md is very short", "README.md")

            # Check for recommended sections
            recommended = [
                "# ",  # Title
                "## Installation",
                "## Usage",
            ]

            for section in recommended:
                if section not in content:
                    self.add_error(
                        "info",
                        f"README missing recommended section: {section}",
                        "README.md",
                    )

        except Exception as e:
            self.add_error("error", f"Error reading README.md: {e}", "README.md")

    def print_results(self):
        """Print validation results"""
        if not self.errors:
            print("✓ Validation passed! No issues found.")
            return

        # Group by severity
        errors = [e for e in self.errors if e.severity == "error"]
        warnings = [e for e in self.errors if e.severity == "warning"]
        infos = [e for e in self.errors if e.severity == "info"]

        if errors:
            print("\nERRORS:")
            for error in errors:
                print(f"  {error}")

        if warnings:
            print("\nWARNINGS:")
            for warning in warnings:
                print(f"  {warning}")

        if infos:
            print("\nINFO:")
            for info in infos:
                print(f"  {info}")

        # Summary
        print("\n" + "=" * 60)
        print(f"Errors: {len(errors)} | Warnings: {len(warnings)} | Info: {len(infos)}")

        if errors:
            print("\n❌ Validation FAILED - fix errors before packaging")
        else:
            print("\n⚠️  Validation passed with warnings")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate Claude Code plugin structure and configuration"
    )

    parser.add_argument(
        "plugin_path", help="Path to plugin directory to validate"
    )

    args = parser.parse_args()

    plugin_path = Path(args.plugin_path)

    print(f"Validating plugin: {plugin_path}")
    print("=" * 60)

    validator = PluginValidator(plugin_path)
    success = validator.validate()
    validator.print_results()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
