#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REQUIRED_MCP_SERVERS = {
    "playwright": {
        "command": "npx",
        "args": ["-y", "@playwright/mcp@latest"],
    },
    "shadcn": {
        "command": "npx",
        "args": ["shadcn@latest", "mcp"],
    },
}

CLAUDE_ENABLED_SERVERS = ["playwright", "shadcn"]

CODEX_BLOCKS = {
    "playwright": '[mcp_servers.playwright]\ncommand = "npx"\nargs = ["-y", "@playwright/mcp@latest"]\n',
    "shadcn": '[mcp_servers.shadcn]\ncommand = "npx"\nargs = ["shadcn@latest", "mcp"]\n',
}

GITIGNORE_CONTENT = """# OS
.DS_Store

# Editors
.idea/
.vscode/

# Node
node_modules/
dist/
build/

# Python
__pycache__/
.pytest_cache/
.venv/
venv/

# Coverage
coverage/
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bootstrap a local project for Codex and/or Claude Code."
    )
    parser.add_argument("--project-root", required=True, help="Target project directory.")
    parser.add_argument(
        "--agent",
        default="auto",
        choices=["auto", "codex", "claude", "both"],
        help="Which runtime to configure.",
    )
    return parser.parse_args()


def skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def template_path() -> Path:
    return skill_dir() / "references" / "instruction-template.md"


def load_template() -> str:
    return template_path().read_text(encoding="utf-8")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def detect_agent(project_root: Path, agent: str) -> str:
    if agent != "auto":
        return agent
    if (project_root / ".claude").exists() or (project_root / "CLAUDE.md").exists():
        return "claude"
    if (project_root / ".codex").exists() or (project_root / "AGENTS.md").exists():
        return "codex"
    return "codex"


def trash_file(project_root: Path, path: Path) -> None:
    trash_dir = project_root / ".ai-bootstrap-trash"
    ensure_dir(trash_dir)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = trash_dir / f"{timestamp}-{path.name}"
    path.replace(backup_path)


def safe_write_text(project_root: Path, path: Path, content: str) -> bool:
    ensure_dir(path.parent)
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if current == content:
            return False
        trash_file(project_root, path)
    path.write_text(content, encoding="utf-8")
    return True


def merge_mcp_json(project_root: Path) -> list[Path]:
    path = project_root / ".mcp.json"
    changed = []
    data = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    servers = data.setdefault("mcpServers", {})
    touched = False
    for name, server in REQUIRED_MCP_SERVERS.items():
        if servers.get(name) != server:
            servers[name] = server
            touched = True
    if touched or not path.exists():
        safe_write_text(project_root, path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        changed.append(path)
    return changed


def merge_claude_settings(project_root: Path) -> list[Path]:
    path = project_root / ".claude" / "settings.local.json"
    changed = []
    data = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    enabled = data.get("enabledMcpjsonServers", [])
    if not isinstance(enabled, list):
        raise ValueError("enabledMcpjsonServers must be a JSON array.")
    for name in CLAUDE_ENABLED_SERVERS:
        if name not in enabled:
            enabled.append(name)
    new_data = dict(data)
    new_data["enableAllProjectMcpServers"] = True
    new_data["enabledMcpjsonServers"] = enabled
    if safe_write_text(
        project_root,
        path,
        json.dumps(new_data, indent=2, ensure_ascii=False) + "\n",
    ):
        changed.append(path)
    return changed


def merge_codex_config(project_root: Path) -> list[Path]:
    path = project_root / ".codex" / "config.toml"
    ensure_dir(path.parent)
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    parts = [current.rstrip()]
    touched = False
    for name, block in CODEX_BLOCKS.items():
        marker = f"[mcp_servers.{name}]"
        if marker not in current:
            parts.append(block.rstrip())
            touched = True
    new_content = "\n\n".join(part for part in parts if part).rstrip() + "\n"
    if touched or not path.exists():
        safe_write_text(project_root, path, new_content)
        return [path]
    return []


def write_instruction_files(project_root: Path, target: str, content: str) -> list[Path]:
    changed = []
    if target in {"codex", "both"}:
        path = project_root / "AGENTS.md"
        if safe_write_text(project_root, path, content):
            changed.append(path)
    if target in {"claude", "both"}:
        path = project_root / "CLAUDE.md"
        if safe_write_text(project_root, path, content):
            changed.append(path)
    return changed


def ensure_gitignore(project_root: Path) -> list[Path]:
    path = project_root / ".gitignore"
    if path.exists():
        return []
    safe_write_text(project_root, path, GITIGNORE_CONTENT)
    return [path]


def run_git(project_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )


def init_git_and_commit(project_root: Path, changed_files: list[Path]) -> list[str]:
    notes = []
    if (project_root / ".git").exists():
        notes.append("Git repository already existed; left it intact.")
        return notes
    init_result = run_git(project_root, ["init"])
    if init_result.returncode != 0:
        notes.append(f"Git init failed: {init_result.stderr.strip() or init_result.stdout.strip()}")
        return notes
    notes.append("Initialized Git repository.")
    relative_paths = [str(path.relative_to(project_root)) for path in changed_files if path.exists()]
    if not relative_paths:
        return notes
    add_result = run_git(project_root, ["add", "--force", *relative_paths])
    if add_result.returncode != 0:
        notes.append(f"Git add failed: {add_result.stderr.strip() or add_result.stdout.strip()}")
        return notes
    commit_result = run_git(project_root, ["commit", "-m", "chore: bootstrap AI agent project"])
    if commit_result.returncode != 0:
        notes.append(
            "Initial commit was not created automatically. "
            f"Reason: {commit_result.stderr.strip() or commit_result.stdout.strip()}"
        )
        return notes
    notes.append("Created initial Git commit: chore: bootstrap AI agent project")
    return notes


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    ensure_dir(project_root)
    target = detect_agent(project_root, args.agent)
    template = load_template()

    changed_files: list[Path] = []
    changed_files.extend(write_instruction_files(project_root, target, template))
    if target in {"claude", "both"}:
        changed_files.extend(merge_mcp_json(project_root))
        changed_files.extend(merge_claude_settings(project_root))
    if target in {"codex", "both"}:
        changed_files.extend(merge_codex_config(project_root))
    changed_files.extend(ensure_gitignore(project_root))

    git_notes = init_git_and_commit(project_root, changed_files)

    print(f"Target runtime: {target}")
    if changed_files:
        print("Updated files:")
        for path in changed_files:
            print(f"- {path.relative_to(project_root)}")
    else:
        print("No file changes were required.")
    for note in git_notes:
        print(note)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"bootstrap_project.py failed: {exc}", file=sys.stderr)
        raise
