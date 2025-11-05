# Full Plugin Template

Complete plugin template combining MCP server, skill, and slash commands.

## Overview

This template provides a complete plugin structure with all components:
- **MCP Server** - External tool integration
- **Skill** - Procedural knowledge and workflows
- **Slash Commands** - Quick user shortcuts

## Structure

```
full-plugin-template/
├── mcp-server/              # MCP server component
│   ├── package.json         # (TypeScript) or
│   ├── pyproject.toml       # (Python)
│   ├── src/ or app/         # Source code
│   └── README.md
├── skill/                   # Skill component
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   ├── assets/
│   └── README.md
├── commands/                # Slash commands
│   ├── command1.md
│   ├── command2.md
│   └── README.md
├── README.md                # Main documentation (this file)
└── ARCHITECTURE.md          # Architecture documentation
```

## Quick Start

1. **Choose your stack**
   - Copy `mcp-server-typescript/` OR `mcp-server-python/`
   - Rename to match your plugin name

2. **Customize each component**
   - **MCP Server**: Add your tools and resources
   - **Skill**: Add workflows and knowledge
   - **Commands**: Add user-facing shortcuts

3. **Integrate components**
   - Commands call MCP tools
   - Skill references MCP tools
   - Commands use skill workflows

4. **Test integration**
   - Test each component individually
   - Test component interactions
   - Verify complete workflows

5. **Package for distribution**
   ```bash
   # Build MCP server
   cd mcp-server && npm run build  # or pip install .

   # Package plugin
   cd .. && zip -r my-plugin.zip .
   ```

## Component Integration

### MCP Server → Skill

**SKILL.md references MCP tools:**
```markdown
## Database Migration Workflow

1. Check pending migrations:
   Use the `get_pending_migrations` tool from database MCP server

2. Review migrations:
   Reference `references/migration_guide.md` for best practices

3. Execute migrations:
   Use the `run_migration` tool for each pending migration
```

### MCP Server → Commands

**Commands call MCP tools:**
```markdown
# db:migrate

Run database migrations.

## Prompt

Use database MCP server to run migrations:

1. Use `get_pending_migrations` tool
2. Display list of pending migrations
3. Ask for confirmation
4. Use `run_migration` tool for each
5. Report results
```

### Skill → Commands

**Commands use skill knowledge:**
```markdown
# deploy:prod

Deploy to production with safety checks.

## Prompt

Deploy to production using deployment skill:

1. Load deployment skill
2. Reference `references/deployment_checklist.md`
3. Verify all checklist items
4. Run deployment script
5. Verify deployment
```

### Complete Integration

```
User Request: "/db:migrate"
       ↓
Slash Command (parses request)
       ↓
Skill (provides workflow and best practices)
       ↓
MCP Server (executes migrations)
       ↓
Results to User
```

## Architecture Patterns

### Pattern 1: Tool-First
MCP server provides all functionality, skill documents usage:

```
MCP: get_users, create_user, update_user, delete_user
Skill: User management best practices
Commands: /user:create, /user:list
```

### Pattern 2: Workflow-First
Skill defines complex workflows, MCP provides primitives:

```
MCP: build, test, deploy (primitives)
Skill: Complete CI/CD workflow combining primitives
Commands: /deploy:prod (executes workflow)
```

### Pattern 3: Balanced
Each component has clear responsibilities:

```
MCP: Database operations
Skill: Schema design patterns, migration strategies
Commands: Quick database operations
```

## Development Workflow

### 1. Start with MCP Server

Define your tools:
```typescript
// What external operations do you need?
- connect_to_database
- run_query
- execute_migration
```

### 2. Add Skill Knowledge

Document workflows:
```markdown
## Migration Workflow
1. Generate migration file
2. Review for safety
3. Test on staging
4. Apply to production
```

### 3. Create Commands

Add shortcuts:
```markdown
# db:migrate - Run migrations
# db:rollback - Rollback migration
# db:schema - Show schema
```

### 4. Integrate

Ensure components work together:
- Commands reference skill workflows
- Skill explains MCP tool usage
- MCP tools do the actual work

## Testing Strategy

### Component Testing

**MCP Server:**
```bash
# Test tools individually
npm test

# Test with Claude Code
mcp add ./mcp-server
```

**Skill:**
```
# Load skill in Claude Code
# Test workflows with realistic scenarios
# Verify all examples work
```

**Commands:**
```
# Execute each command
/command-name test-args

# Verify output is correct
# Test error handling
```

### Integration Testing

```
# Test complete workflows
1. Use command that calls skill
2. Skill should reference MCP tools
3. MCP tools should execute correctly
4. Results should flow back to user

# Verify all integration points work
```

## Configuration

### MCP Server Config
```json
{
  "mcpServers": {
    "my-plugin": {
      "command": "node",
      "args": ["path/to/mcp-server/dist/index.js"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

### Skill Installation
```bash
cp -r skill/ ~/.claude/skills/my-plugin-skill/
```

### Commands Installation
```bash
cp commands/*.md ~/.claude/commands/
```

## Documentation Requirements

### README.md (Main)
- Plugin overview and features
- Installation instructions
- Quick start guide
- Component descriptions
- Usage examples

### ARCHITECTURE.md
- Component relationships
- Integration patterns
- Data flow diagrams
- Design decisions
- Extension points

### Component READMEs
- MCP Server README: Tool documentation
- Skill README: Workflow documentation
- Commands README: Command reference

## Distribution

### Package Structure
```
my-plugin-v1.0.0.zip
├── README.md                # Installation and usage
├── ARCHITECTURE.md          # Technical docs
├── mcp-server/
│   ├── dist/               # Pre-built (or installation instructions)
│   └── README.md
├── skill/
│   ├── SKILL.md
│   └── ...
└── commands/
    └── *.md
```

### Installation Instructions
```markdown
# Installation

1. Extract plugin:
   unzip my-plugin-v1.0.0.zip

2. Install MCP server:
   cd mcp-server
   npm install -g .    # or: pip install .

3. Add to Claude Code config:
   [config example]

4. Install skill:
   cp -r skill/ ~/.claude/skills/my-plugin/

5. Install commands:
   cp commands/*.md ~/.claude/commands/
```

## Example Plugins

### Database Management Plugin
```
Components:
- MCP: Database tools (connect, query, migrate)
- Skill: Schema design, migration workflows
- Commands: /db:migrate, /db:query, /db:schema
```

### API Testing Plugin
```
Components:
- MCP: HTTP client, response validator
- Skill: API testing best practices
- Commands: /api:test, /api:validate
```

### Deployment Plugin
```
Components:
- MCP: Cloud deployment tools
- Skill: Deployment workflows, checklists
- Commands: /deploy:dev, /deploy:staging, /deploy:prod
```

## Best Practices

1. **Clear Separation**: Each component has distinct responsibility
2. **Good Integration**: Components work together smoothly
3. **Complete Documentation**: Every component well-documented
4. **Tested Thoroughly**: All features and integrations tested
5. **Easy Installation**: Clear, simple installation process
6. **Helpful Examples**: Concrete usage examples throughout

## Resources

- [MCP Server Guide](../../references/mcp_server_guide.md)
- [Skill Guide](../../references/skill_guide.md)
- [Slash Command Guide](../../references/slash_command_guide.md)
- [Architecture Patterns](../../references/architecture_patterns.md)
- [Best Practices](../../references/best_practices.md)
