---
name: project-agent-bootstrap
description: Bootstrap new or existing local projects for AI-assisted development by creating an `AGENTS.md` for Codex or a `CLAUDE.md` for Claude Code from the bundled rules template, wiring project-local MCP servers for Playwright and shadcn/ui, and initializing Git with a first checkpoint commit when needed. Use whenever the user asks to start a project with agent instructions, scaffold a repo for Codex or Claude Code, add local MCP servers to a project, or standardize an AI-ready project workspace before implementation begins.
---

# Project Agent Bootstrap

## Overview

Use this skill to turn a plain folder into an AI-ready project workspace. It writes the main instruction file from the bundled template, configures local MCP servers for the selected runtime, and bootstraps Git safely.

## Quick Start

Run the bootstrap script first:

```bash
python3 ./project-agent-bootstrap/scripts/bootstrap_project.py \
  --project-root /absolute/path/to/project \
  --agent codex
```

Valid `--agent` values:

- `codex`: create `AGENTS.md` and `.codex/config.toml`
- `claude`: create `CLAUDE.md`, `.mcp.json`, and `.claude/settings.local.json`
- `both`: create both instruction files and both runtime configs
- `auto`: infer runtime from the existing project; default to `codex`

## Workflow

1. Decide which runtime the project needs: Codex, Claude Code, or both.
2. Run `scripts/bootstrap_project.py` with the target project root.
3. Review the generated instruction file and keep the bundled policy intact unless the user explicitly wants changes.
4. If the project already had local config, keep the merged result. Do not strip user-defined MCP entries.
5. Continue implementation inside the bootstrapped repo.

## Output Contract

Generate these files:

- `AGENTS.md` or `CLAUDE.md`: copy the bundled template from [references/instruction-template.md](references/instruction-template.md)
- `.codex/config.toml`: add project-local `playwright` and `shadcn` servers for Codex
- `.mcp.json`: add project-local `playwright` and `shadcn` servers for Claude Code
- `.claude/settings.local.json`: enable project MCP servers for Claude Code
- `.gitignore`: create a minimal bootstrap ignore file when the repo is new
- `.git`: initialize a Git repository if missing and create an initial commit when possible

## Guardrails

- Do not hard-delete replaced files. The script moves overwritten instruction files into `.ai-bootstrap-trash/`.
- Merge existing `.mcp.json`, `.claude/settings.local.json`, and `.codex/config.toml` instead of replacing them wholesale.
- Keep the package-version rule in the generated instruction file: every external package and library version must be checked on the internet before installation or update.
- Do not claim UI work is done just because code compiles. The generated instruction file already requires Playwright MCP verification for UI projects.

## Resources

- Use [scripts/bootstrap_project.py](scripts/bootstrap_project.py) for deterministic project setup.
- Read [references/instruction-template.md](references/instruction-template.md) only if you need to inspect or adjust the bundled rules text.

## Example Prompts

- "Create a new Codex-ready Next.js project here and set up `AGENTS.md` with local Playwright and shadcn MCP."
- "Bootstrap this repo for Claude Code with `CLAUDE.md` and project-local MCP servers."
- "Standardize this existing folder for AI agents before we start building."
