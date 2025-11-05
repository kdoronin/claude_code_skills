# Slash Command Development Guide

Comprehensive guide for creating effective slash commands for Claude Code.

## What is a Slash Command?

A slash command is a user-defined operation that:
- Starts with `/` (e.g., `/deploy`, `/test`, `/review`)
- Expands to a full prompt when executed
- Provides quick shortcuts for common operations
- Can accept arguments for parameterization

Slash commands make frequent operations fast and consistent.

## When to Create Slash Commands

Create slash commands when you need:
- Quick shortcuts for repeated operations
- Standardized workflows with consistent execution
- User-facing operations with simple parameters
- Integration with existing skills or MCP servers
- Command-line style interface for specific tasks

**Good Use Cases:**
- `/deploy:prod` - Deploy to production
- `/test:unit` - Run unit tests
- `/review:security` - Security-focused code review
- `/db:migrate` - Run database migrations
- `/format:code` - Format code with standards

**Bad Use Cases:**
- Complex multi-step workflows (use skills instead)
- Operations requiring extensive configuration (use skills)
- Infrequent operations (not worth a command)

## Command Structure

### File Location

```
.claude/
└── commands/
    ├── deploy.md
    ├── test.md
    └── review.md
```

### File Format

Each command is a markdown file with two sections:

```markdown
# Command Name

Brief description of what this command does.

## Prompt

The actual prompt that gets executed when command runs.
This can include parameters, references to skills, and tool usage.
```

## Basic Command Pattern

### Simple Command

```markdown
# format

Format code according to project standards.

## Prompt

Format the code in the current file according to project standards:
1. Run the formatter (prettier/black/etc based on file type)
2. Apply linting rules
3. Organize imports
4. Report any remaining issues
```

### Command with Arguments

```markdown
# test

Run tests with optional scope argument.

## Prompt

Run tests {{args}}.

If no arguments provided, run all tests.
If scope provided (unit/integration/e2e), run only those tests.

Steps:
1. Determine test scope from arguments
2. Run appropriate test command
3. Report results with coverage
4. Highlight any failures
```

**Usage:**
```
/test unit
/test integration
/test
```

### Command with File Context

```markdown
# review

Perform code review on current file or specified files.

## Prompt

Perform a comprehensive code review {{args}}.

Review focus areas:
- Code organization and structure
- Naming conventions and clarity
- Error handling
- Test coverage
- Security considerations
- Performance implications

If files specified in args, review those files.
If no args, review currently open file.

Use the code-review skill for detailed checklist.
```

## Advanced Patterns

### Command with MCP Integration

```markdown
# db:migrate

Run database migrations.

## Prompt

Run database migrations using the database MCP server.

Steps:
1. Use `connect_db` tool to establish connection
2. Use `get_pending_migrations` tool to check pending migrations
3. For each pending migration:
   - Display migration details
   - Use `run_migration` tool to execute
   - Verify success
4. Report final migration status

Handle errors gracefully and allow rollback if issues occur.
```

### Command with Skill Integration

```markdown
# api:test

Test API endpoint with validation.

## Prompt

Test API endpoint using the api-testing skill.

Arguments expected: endpoint path (e.g., /users, /auth/login)

Workflow:
1. Load api-testing skill
2. Reference API schema from skill resources
3. Execute test for specified endpoint
4. Validate response against schema
5. Report results with detailed output
```

### Parameterized Command

```markdown
# deploy

Deploy application to specified environment.

## Prompt

Deploy application to {{args}} environment.

Supported environments: dev, staging, prod

Pre-deployment checks:
1. Verify all tests pass
2. Check branch is up to date
3. Confirm no uncommitted changes (for prod)
4. Review environment-specific configuration

Deployment steps:
1. Build for target environment
2. Run pre-deployment validations
3. Execute deployment
4. Run smoke tests
5. Verify deployment success
6. Update deployment log

For production: require explicit confirmation before proceeding.
```

**Usage:**
```
/deploy dev
/deploy staging
/deploy prod
```

### Multi-Argument Command

```markdown
# scaffold

Generate component scaffolding.

## Prompt

Generate scaffolding for: {{args}}

Expected format: <type> <name> [options]
Examples:
- component UserProfile
- api-route /users auth
- model User --with-tests

Steps:
1. Parse arguments to determine type, name, and options
2. Use appropriate template from assets
3. Generate files in correct location
4. Apply naming conventions
5. Create associated tests if --with-tests option
6. Report created files and next steps
```

## Command Naming Conventions

### Single-Word Commands

```
/test
/build
/deploy
/format
/lint
/review
```

### Namespaced Commands

```
/api:test
/api:validate
/api:mock

/db:migrate
/db:seed
/db:rollback

/deploy:dev
/deploy:staging
/deploy:prod
```

### Best Practices

- **Short and Memorable** - Easy to type quickly
- **Consistent Naming** - Follow project conventions
- **Namespace Related Commands** - Use `:` for grouping
- **Avoid Conflicts** - Don't override built-in commands
- **Descriptive** - Name clearly indicates action

## Argument Handling

### No Arguments

```markdown
## Prompt

Run all tests with full coverage report.

[Command logic that doesn't need parameters]
```

### Optional Arguments

```markdown
## Prompt

Run tests {{args}}.

If args provided:
- Use as test scope or pattern
Otherwise:
- Run all tests with default settings
```

### Required Arguments

```markdown
## Prompt

Deploy to {{args}} environment.

If no environment specified:
- Display error: "Environment required (dev/staging/prod)"
- Do not proceed

Otherwise:
- Proceed with deployment to specified environment
```

### Argument Parsing

```markdown
## Prompt

Process command arguments: {{args}}

Parse arguments as key=value pairs:
{{args}} should be in format: key1=value1 key2=value2

Example: /command env=prod version=2.0.1

Extract:
1. Split args on spaces
2. Parse each as key=value
3. Validate required keys present
4. Use in subsequent operations
```

## Integration Patterns

### With Skills

```markdown
# security-audit

Run security audit using security skill.

## Prompt

Perform security audit using the security-engineer skill.

Scope: {{args}} or entire codebase if no args

Steps:
1. Activate security-engineer skill
2. Load security checklist from skill references
3. Run automated security scanners
4. Review code for common vulnerabilities
5. Generate security report
6. Provide remediation recommendations
```

### With MCP Servers

```markdown
# perf:analyze

Analyze performance using performance MCP tools.

## Prompt

Analyze performance for {{args}}.

Use performance-monitoring MCP server:
1. `start_profiler` tool to begin profiling
2. Execute target code/operation
3. `stop_profiler` tool to end profiling
4. `get_profile_results` tool to retrieve data
5. Analyze results and identify bottlenecks
6. Provide optimization recommendations
```

### With Other Commands

```markdown
# pre-commit

Run pre-commit checks.

## Prompt

Run pre-commit validation checks:

1. Execute `/format` command to format code
2. Execute `/lint` command to check style
3. Execute `/test unit` command for quick tests
4. Verify no uncommitted changes to critical files
5. Check commit message format

If all checks pass: approve commit
If any check fails: report issues and block commit
```

## Command Documentation

### In-Command Documentation

```markdown
# deploy

Deploy application to target environment.

## Prompt

Deploy application to {{args}} environment.

USAGE:
  /deploy <environment> [options]

ENVIRONMENTS:
  dev       - Development environment
  staging   - Staging environment
  prod      - Production environment

OPTIONS:
  --skip-tests    Skip test execution
  --force         Force deployment
  --dry-run       Simulate deployment

EXAMPLES:
  /deploy dev
  /deploy prod --dry-run
  /deploy staging --skip-tests

[Deployment logic continues...]
```

### README for Commands

Create `.claude/commands/README.md`:

```markdown
# Custom Commands

## Deployment Commands

### /deploy
Deploy application to specified environment.
Usage: `/deploy <env>`

### /rollback
Rollback to previous deployment.
Usage: `/rollback <env>`

## Testing Commands

### /test
Run test suites.
Usage: `/test [scope]`

### /coverage
Generate coverage report.
Usage: `/coverage`

## Development Commands

### /format
Format code.
Usage: `/format`

### /lint
Run linter.
Usage: `/lint [path]`
```

## Error Handling

### Validation

```markdown
## Prompt

Validate inputs before executing: {{args}}

Required validations:
1. Check environment is valid (dev/staging/prod)
2. Verify user has permissions for target environment
3. Confirm deployment branch is correct
4. Validate configuration files exist

If validation fails:
- Display clear error message
- Explain what was wrong
- Suggest correct usage
- Do not proceed with operation

Only proceed if all validations pass.
```

### Graceful Degradation

```markdown
## Prompt

Execute operation with fallback handling: {{args}}

Primary approach:
1. Try using MCP server tool
2. Execute and check for errors

If MCP tool fails:
1. Log the error
2. Fall back to native implementation
3. Warn user about fallback usage
4. Complete operation with reduced functionality

Report which approach was used and why.
```

### User Confirmation

```markdown
## Prompt

Deploy to production: {{args}}

⚠️ PRODUCTION DEPLOYMENT - Confirmation Required

Display:
1. Target environment: PRODUCTION
2. Current branch and commit
3. Changes being deployed
4. Services that will be affected

Ask user to confirm:
"Type 'CONFIRM' to proceed with production deployment"

If confirmed:
- Proceed with deployment
Otherwise:
- Cancel and explain how to retry
```

## Testing Commands

### Manual Testing

```bash
# In Claude Code, test command:
/deploy dev

# Verify:
# - Command triggers correctly
# - Arguments are parsed
# - Expected behavior occurs
# - Error handling works
# - Output is clear and useful
```

### Testing Checklist

- [ ] Command triggers with correct name
- [ ] Arguments parse correctly
- [ ] Prompt executes expected workflow
- [ ] Integration with skills/MCP works
- [ ] Error handling is graceful
- [ ] Output is clear and actionable
- [ ] Documentation is accurate

## Common Patterns

### Quick Operation

```markdown
# fix

Quick fix common issues.

## Prompt

Analyze and fix common issues in current file:
1. Fix import errors
2. Resolve type errors
3. Fix formatting
4. Remove unused variables
5. Apply quick fixes from linter

Report what was fixed.
```

### Information Display

```markdown
# status

Display project status.

## Prompt

Display comprehensive project status:

Git Status:
- Current branch
- Uncommitted changes
- Unpushed commits

Tests:
- Last test run results
- Current coverage

Build:
- Last build status
- Build configuration

Dependencies:
- Outdated packages
- Security vulnerabilities

Present in organized, readable format.
```

### Workflow Automation

```markdown
# release

Automate release process.

## Prompt

Execute release workflow: {{args}}

Expected: version number (e.g., 1.2.3)

Release steps:
1. Validate version format
2. Update version in package files
3. Run full test suite
4. Build production artifacts
5. Create git tag
6. Push tag to remote
7. Trigger CI/CD pipeline
8. Generate release notes

Confirm each step before proceeding.
```

## Best Practices

### Command Design

1. **Single Responsibility** - One command, one clear purpose
2. **Predictable Behavior** - Same inputs = same outputs
3. **Clear Documentation** - Usage examples and descriptions
4. **Error Messages** - Helpful error messages with guidance
5. **Idempotency** - Safe to run multiple times when possible

### User Experience

1. **Fast Execution** - Commands should be quick
2. **Progress Feedback** - Show what's happening
3. **Clear Output** - Organized, readable results
4. **Helpful Errors** - Guide user to resolution
5. **Confirmation for Danger** - Require confirmation for destructive operations

### Integration

1. **Leverage Skills** - Use existing skills for workflows
2. **Use MCP Tools** - Integrate with MCP servers
3. **Compose Commands** - Chain commands when appropriate
4. **Consistent Conventions** - Match project patterns
5. **Share Context** - Commands can reference each other

## Examples Library

### Development Commands

```markdown
# init

Initialize new project component.

## Prompt

Initialize new component: {{args}}

Parse component type and name from args.

Steps:
1. Create component directory structure
2. Generate component files from templates
3. Add component to index
4. Create test file
5. Update documentation

Report created files and next steps.
```

### Testing Commands

```markdown
# test:watch

Run tests in watch mode.

## Prompt

Start test watcher for {{args}} or all tests.

1. Determine test scope from args
2. Start test runner in watch mode
3. Monitor for file changes
4. Re-run affected tests on changes
5. Display results in real-time

Press Ctrl+C to stop watching.
```

### Build Commands

```markdown
# build:analyze

Analyze build output.

## Prompt

Build and analyze bundle size and composition.

1. Run production build
2. Generate bundle analysis
3. Identify large dependencies
4. Find duplicate code
5. Suggest optimizations

Display visual bundle analysis and recommendations.
```

### Database Commands

```markdown
# db:reset

Reset database to clean state.

## Prompt

Reset database: {{args}}

⚠️ WARNING: This will delete all data!

Steps:
1. Request confirmation
2. Drop all tables
3. Run all migrations
4. Seed with default data
5. Verify database state

Report completion and new state.
```

## Command Distribution

Commands are typically distributed as part of:
- **Plugin packages** - Bundled with skills and MCP servers
- **Project templates** - Included in starter templates
- **Standalone packages** - Shared command collections

### Installation

Users add commands to `.claude/commands/`:
```bash
cp my-commands/*.md ~/.claude/commands/
```

### Documentation

Include README with:
- Command list and descriptions
- Usage examples
- Integration requirements
- Configuration needed

## Summary

Slash commands provide quick, consistent shortcuts for common operations. Design them to:
- Be fast and focused
- Integrate with skills and MCP servers
- Handle errors gracefully
- Provide clear feedback
- Follow consistent patterns

Good commands make Claude Code usage more efficient and pleasant.
