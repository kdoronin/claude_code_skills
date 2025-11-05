#!/usr/bin/env python3
"""
Plugin Initialization Script

Creates plugin scaffolding from templates.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Optional


PLUGIN_TYPES = {
    "mcp-ts": "MCP Server (TypeScript)",
    "mcp-py": "MCP Server (Python)",
    "skill": "Skill",
    "command": "Slash Command",
    "full": "Full Plugin (MCP + Skill + Commands)",
}


def get_templates_dir() -> Path:
    """Get the templates directory path"""
    script_dir = Path(__file__).parent
    return script_dir.parent / "assets" / "templates"


def create_plugin(
    plugin_name: str, plugin_type: str, output_dir: Optional[str] = None
) -> int:
    """
    Create plugin from template

    Args:
        plugin_name: Name of the plugin to create
        plugin_type: Type of plugin (mcp-ts, mcp-py, skill, command, full)
        output_dir: Output directory (default: current directory)

    Returns:
        Exit code (0 for success)
    """
    # Determine output path
    if output_dir:
        output_path = Path(output_dir) / plugin_name
    else:
        output_path = Path.cwd() / plugin_name

    if output_path.exists():
        print(f"Error: Directory already exists: {output_path}", file=sys.stderr)
        return 1

    # Get template directory
    templates_dir = get_templates_dir()

    if not templates_dir.exists():
        print(f"Error: Templates directory not found: {templates_dir}", file=sys.stderr)
        return 1

    # Map plugin type to template directory
    template_map = {
        "mcp-ts": "mcp-server-typescript",
        "mcp-py": "mcp-server-python",
        "skill": "skill",
        "command": "slash-command",
        "full": "full-plugin",
    }

    template_name = template_map.get(plugin_type)
    if not template_name:
        print(f"Error: Unknown plugin type: {plugin_type}", file=sys.stderr)
        return 1

    template_path = templates_dir / template_name

    if not template_path.exists():
        print(f"Error: Template not found: {template_path}", file=sys.stderr)
        return 1

    # Create plugin from template
    try:
        print(f"Creating {PLUGIN_TYPES[plugin_type]} plugin: {plugin_name}")
        print(f"Template: {template_name}")
        print(f"Output: {output_path}")

        if plugin_type == "full":
            # For full plugin, create structure and copy components
            output_path.mkdir(parents=True)

            print("\nCopying MCP server template (choose TypeScript or Python)...")
            print("  Copying TypeScript version...")
            mcp_ts_src = templates_dir / "mcp-server-typescript"
            mcp_ts_dst = output_path / "mcp-server-typescript"
            shutil.copytree(mcp_ts_src, mcp_ts_dst)

            print("  Copying Python version...")
            mcp_py_src = templates_dir / "mcp-server-python"
            mcp_py_dst = output_path / "mcp-server-python"
            shutil.copytree(mcp_py_src, mcp_py_dst)

            print("\nCopying skill template...")
            skill_src = templates_dir / "skill"
            skill_dst = output_path / "skill"
            shutil.copytree(skill_src, skill_dst)

            print("Copying command template...")
            command_src = templates_dir / "slash-command"
            command_dst = output_path / "commands"
            shutil.copytree(command_src, command_dst)

            print("\nCopying full plugin README...")
            readme_src = templates_dir / "full-plugin" / "README.md"
            readme_dst = output_path / "README.md"
            shutil.copy(readme_src, readme_dst)

        else:
            # For single component, copy template
            shutil.copytree(template_path, output_path)

        print(f"\n✓ Plugin created successfully: {output_path}")

        # Print next steps
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)

        if plugin_type == "mcp-ts":
            print(f"""
1. Install dependencies:
   cd {plugin_name}
   npm install

2. Customize the server:
   - Edit src/index.ts to add your tools
   - Update package.json with your details

3. Build and test:
   npm run build
   npm start

4. Add to Claude Code config
""")
        elif plugin_type == "mcp-py":
            print(f"""
1. Install dependencies:
   cd {plugin_name}
   pip install -e .

2. Customize the server:
   - Edit app/main.py to add your tools
   - Update pyproject.toml with your details

3. Test:
   python -m app.main

4. Add to Claude Code config
""")
        elif plugin_type == "skill":
            print(f"""
1. Customize the skill:
   cd {plugin_name}
   - Edit SKILL.md with your content
   - Add scripts to scripts/
   - Add references to references/
   - Add assets to assets/

2. Test the skill

3. Install:
   cp -r {plugin_name}/ ~/.claude/skills/
""")
        elif plugin_type == "command":
            print(f"""
1. Customize the command:
   cd {plugin_name}
   - Rename example-command.md
   - Edit with your command logic

2. Install:
   cp *.md ~/.claude/commands/

3. Test:
   /your-command [args]
""")
        elif plugin_type == "full":
            print(f"""
1. Choose MCP server language:
   cd {plugin_name}
   - Keep either mcp-server-typescript/ OR mcp-server-python/
   - Delete the other one
   - Rename kept one to just 'mcp-server/'

2. Customize each component:
   - MCP server: Add tools and resources
   - Skill: Add workflows and knowledge
   - Commands: Add user shortcuts

3. Integrate components:
   - Make commands call MCP tools
   - Make skill reference MCP tools
   - Test integration

4. See README.md for detailed instructions
""")

        return 0

    except Exception as e:
        print(f"Error creating plugin: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Initialize a new Claude Code plugin from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available plugin types:
  mcp-ts    - MCP Server (TypeScript)
  mcp-py    - MCP Server (Python/FastMCP)
  skill     - Skill with workflows and knowledge
  command   - Slash command
  full      - Complete plugin with all components

Examples:
  # Create TypeScript MCP server
  python init_plugin.py my-api-client --type mcp-ts

  # Create skill
  python init_plugin.py code-review --type skill

  # Create full plugin
  python init_plugin.py database-toolkit --type full

  # Specify output directory
  python init_plugin.py my-plugin --type skill --output ~/projects
""",
    )

    parser.add_argument("name", help="Plugin name")

    parser.add_argument(
        "--type",
        choices=list(PLUGIN_TYPES.keys()),
        required=True,
        help="Plugin type to create",
    )

    parser.add_argument(
        "--output", "-o", help="Output directory (default: current directory)"
    )

    args = parser.parse_args()

    return create_plugin(args.name, args.type, args.output)


if __name__ == "__main__":
    sys.exit(main())
