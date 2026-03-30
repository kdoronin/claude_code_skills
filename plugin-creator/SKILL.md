---
name: plugin-creator
description: "Scaffolds complete Claude Code plugins from requirements — MCP servers (TypeScript/Python), skills, slash commands, or combinations. Use when the user wants to build a plugin, create an MCP server, add a slash command, develop a skill, scaffold a tool for Claude Code, or extend Claude Code with custom functionality."
---

# Plugin Creator

Scaffolds and packages production-ready Claude Code plugins by analyzing requirements and selecting the right component mix.

## Workflow

### 1. Analyze Requirements → Pick Architecture

| Component | When to Use |
|-----------|-------------|
| **MCP Server** | External tool/service integration, stateful operations, real-time data |
| **Skill** | Procedural workflows, domain knowledge, multi-step processes |
| **Slash Command** | Quick actions, command shortcuts |
| **Combination** | Complex plugins needing multiple interaction patterns |

### 2. Scaffold

```bash
python scripts/init_plugin.py <plugin-name> --type <mcp|skill|command|full>
```

Templates in `assets/templates/`:
- `mcp-server-typescript/` — TypeScript MCP server (JS ecosystem, web APIs)
- `mcp-server-python/` — Python FastMCP server (data science, ML tools)
- `skill/` — Skill with SKILL.md, scripts, references
- `slash-command/` — Command file for `.claude/commands/`

### 3. Implement

For each component, follow the detailed guide:
- **MCP servers:** [references/mcp_server_guide.md](references/mcp_server_guide.md) — define tools, resources, handlers, config
- **Skills:** [references/skill_guide.md](references/skill_guide.md) — frontmatter, triggers, procedures, bundled resources
- **Slash commands:** [references/slash_command_guide.md](references/slash_command_guide.md) — command file, params, prompts

### 4. Integrate (multi-component plugins)

- [ ] MCP tools referenced in skill instructions
- [ ] Slash commands call appropriate MCP tools
- [ ] Consistent naming across components
- [ ] Unified configuration (single config file where possible)

### 5. Validate and Package

```bash
# Validate structure, code quality, docs
python scripts/validate_plugin.py <plugin-path>

# Package for distribution
python scripts/package_plugin.py <plugin-path> [output-dir]
```

If `validate_plugin.py` reports errors: fix structural issues first (missing frontmatter, broken references), then re-run. Common errors: missing SKILL.md fields, unreferenced scripts, incomplete README.

**Output structure:**
```
my-plugin/
├── README.md
├── mcp-server/    (if applicable)
├── skill/         (if applicable)
└── commands/      (if applicable)
```

## References

- [references/best_practices.md](references/best_practices.md) — error handling, security, config management
- [references/architecture_patterns.md](references/architecture_patterns.md) — single-responsibility, composition, scaling
