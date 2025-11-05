# Slash Command Template

Template for creating Claude Code slash commands.

## Quick Start

1. **Copy template**
   ```bash
   cp example-command.md your-command.md
   ```

2. **Customize the command**
   - Replace `command-name` with your command name
   - Update description
   - Write command prompt
   - Add examples

3. **Install command**
   ```bash
   cp your-command.md ~/.claude/commands/
   ```

4. **Test command**
   ```
   /your-command [arguments]
   ```

## Command Structure

```markdown
# command-name            ← Command name (used as /command-name)

Brief description        ← One-line description

## Prompt                 ← Required section

Command execution logic  ← What happens when command runs
```

## Naming Conventions

**Good command names:**
- `/deploy` - Clear, short action
- `/test:unit` - Namespaced for related commands
- `/db:migrate` - Category prefix for organization
- `/api:test` - Clear category and action

**Bad command names:**
- `/d` - Too short, unclear
- `/do-the-deployment-thing` - Too long
- `/testunit` - Missing namespace separator
- `/api_test` - Use colon, not underscore

## Using Arguments

### No Arguments
```markdown
## Prompt

Run all tests with full coverage.
```

### Optional Arguments
```markdown
## Prompt

Run tests {{args}}.

If args provided: use as test filter
Otherwise: run all tests
```

### Required Arguments
```markdown
## Prompt

Deploy to {{args}} environment.

If no environment specified:
  Display: "Usage: /deploy <environment>"
  Stop

Valid environments: dev, staging, prod
```

### Parsing Arguments
```markdown
## Prompt

Process arguments: {{args}}

Expected format: key=value pairs
Example: env=prod version=1.2.3

Steps:
1. Split {{args}} on spaces
2. Parse each as key=value
3. Extract environment and version
4. Proceed with deployment
```

## Integration Patterns

### With Skills
```markdown
## Prompt

Use the deployment-skill for deployment workflow.

Steps:
1. Load deployment skill
2. Reference deployment_checklist.md
3. Run deployment script
4. Verify with health check
```

### With MCP Tools
```markdown
## Prompt

Deploy using cloud MCP server.

Steps:
1. Use `build_image` tool
2. Use `push_to_registry` tool
3. Use `deploy_service` tool with {{args}} environment
4. Use `health_check` tool to verify
```

### Command Composition
```markdown
## Prompt

Run pre-deployment checks:

1. Execute /test command
2. Execute /lint command
3. Execute /build command

If all pass: proceed with deployment
Otherwise: stop and report failures
```

## Error Handling

```markdown
## Prompt

Validate inputs: {{args}}

Required: environment (dev/staging/prod)

If environment missing:
  Display: "Error: Environment required"
  Display: "Usage: /deploy <environment>"
  Stop

If environment invalid:
  Display: "Error: Invalid environment '{{args}}'"
  Display: "Valid options: dev, staging, prod"
  Stop

Proceed with deployment to {{args}}
```

## Best Practices

### Clear Feedback
```markdown
Good:
✓ Tests passed (45/45)
✓ Build complete
→ Deploying to production...
✓ Deployment successful

Bad:
Running...
Done.
```

### Progress Indication
```markdown
Deploying to staging...
1. ✓ Running tests
2. ✓ Building image
3. → Pushing to registry
4. ⏳ Deploying service
5. ⏳ Running health checks
```

### Helpful Errors
```markdown
Good:
Error: Tests failed (3 failures)
Run '/test:unit --verbose' to see details

Bad:
Error
```

### Confirmation for Dangerous Operations
```markdown
⚠️ PRODUCTION DEPLOYMENT

This will deploy to PRODUCTION environment.
Type 'CONFIRM' to proceed.

[Wait for user input]
```

## Examples

### Simple Command
```markdown
# format

Format code according to project standards.

## Prompt

Format code in current file:
1. Run appropriate formatter (prettier/black/etc)
2. Apply project style rules
3. Report changes made
```

### Parameterized Command
```markdown
# deploy

Deploy to specified environment.

## Prompt

Deploy to {{args}} environment.

Environments: dev, staging, prod

Steps:
1. Validate environment
2. Run pre-deploy checks
3. Build and deploy
4. Verify deployment
```

### Integrated Command
```markdown
# db:migrate

Run database migrations using database skill.

## Prompt

Run database migrations using database MCP server.

Steps:
1. Use `get_pending_migrations` tool
2. Display pending migrations
3. Ask for confirmation
4. Use `run_migration` tool for each
5. Report results
```

## Installation

Place command files in:
```
~/.claude/commands/your-command.md
```

Or for project-specific commands:
```
your-project/.claude/commands/your-command.md
```

## Testing Checklist

- [ ] Command name is clear and follows conventions
- [ ] Description accurately describes what command does
- [ ] Arguments are documented and validated
- [ ] Error messages are clear and helpful
- [ ] Integration with skills/MCP works correctly
- [ ] Examples demonstrate usage accurately
- [ ] Dangerous operations require confirmation

## Resources

- [Slash Command Guide](../../references/slash_command_guide.md)
- [Best Practices](../../references/best_practices.md)
