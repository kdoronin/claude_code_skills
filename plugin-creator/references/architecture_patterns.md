# Plugin Architecture Patterns

Comprehensive guide to architectural patterns for Claude Code plugins.

## Plugin Architecture Overview

### Component Types

```
Plugin Components:
├── MCP Server    - Tool/resource provider
├── Skill         - Knowledge and workflows
└── Slash Command - Quick shortcuts
```

**When to use each:**

| Component | Purpose | Best For |
|-----------|---------|----------|
| MCP Server | External integration, stateful ops | APIs, databases, external tools |
| Skill | Procedural knowledge, workflows | Processes, best practices, domain knowledge |
| Slash Command | Quick user-facing operations | Shortcuts, common commands |

## Single-Component Patterns

### Pattern 1: Pure MCP Server

**When to Use:**
- External service integration only
- No complex workflows needed
- Tool-focused functionality

**Example: Weather Service**
```
weather-mcp/
├── package.json
├── src/
│   ├── index.ts
│   ├── tools/
│   │   ├── getCurrentWeather.ts
│   │   ├── getForecast.ts
│   │   └── getHistorical.ts
│   └── config/
│       └── api.ts
└── README.md
```

**Implementation:**
```typescript
// tools/getCurrentWeather.ts
export const getCurrentWeather = {
  name: "get_current_weather",
  description: "Get current weather for a location",
  inputSchema: {
    type: "object",
    properties: {
      location: { type: "string" },
      units: { type: "string", enum: ["metric", "imperial"] }
    },
    required: ["location"]
  }
};

export async function handleGetCurrentWeather(args: any) {
  const weather = await weatherAPI.getCurrent(args.location, args.units);
  return { content: [{ type: "text", text: JSON.stringify(weather) }] };
}
```

**Use Cases:**
- API wrappers (GitHub, Slack, Jira)
- Database connectors
- Cloud service integrations
- File format converters

### Pattern 2: Pure Skill

**When to Use:**
- Knowledge-based only
- No external integrations
- Procedural workflows

**Example: Code Review Guidelines**
```
code-review-skill/
├── SKILL.md
├── references/
│   ├── review_checklist.md
│   ├── security_checklist.md
│   ├── style_guide.md
│   └── examples.md
└── assets/
    └── templates/
        └── review-template.md
```

**SKILL.md Structure:**
```markdown
---
name: code-review
description: Systematic code review workflows and checklists. Use when reviewing pull requests, conducting code audits, or establishing review standards.
---

# Code Review Skill

## Review Workflow

### Pre-Review
1. Read PR description
2. Review linked issues
3. Check CI/CD status

### Code Review
1. Reference `references/review_checklist.md`
2. Check security with `references/security_checklist.md`
3. Verify style per `references/style_guide.md`

### Feedback
Use template from `assets/templates/review-template.md`
```

**Use Cases:**
- Best practices guides
- Process documentation
- Style guides
- Workflow templates

### Pattern 3: Pure Slash Commands

**When to Use:**
- Simple shortcuts only
- No complex state
- Quick user actions

**Example: Development Shortcuts**
```
.claude/commands/
├── format.md
├── lint.md
├── test.md
└── build.md
```

**Command Example:**
```markdown
# test

Run project tests with optional scope.

## Prompt

Run tests {{args}}.

Parse args as test scope (unit/integration/e2e/all).
Default to all tests if no args.

Steps:
1. Determine scope
2. Run appropriate test command
3. Display results with coverage
4. Highlight failures
```

**Use Cases:**
- Development shortcuts
- Build commands
- Simple operations

## Multi-Component Patterns

### Pattern 4: MCP + Skill

**When to Use:**
- External tools + procedural knowledge
- Complex workflows with tool usage
- Best practices for tool integration

**Example: Database Management**
```
database-plugin/
├── mcp-server/
│   ├── package.json
│   └── src/
│       ├── index.ts
│       └── tools/
│           ├── connect.ts
│           ├── query.ts
│           ├── migrate.ts
│           └── schema.ts
└── skill/
    ├── SKILL.md
    ├── references/
    │   ├── migration_guide.md
    │   ├── schema_patterns.md
    │   └── optimization_tips.md
    └── scripts/
        ├── generate_migration.py
        └── validate_schema.py
```

**Integration Pattern:**
```markdown
# SKILL.md

## Database Migration Workflow

### Prerequisites
Ensure database MCP server is configured.

### Migration Process

1. **Generate Migration**
   ```bash
   python scripts/generate_migration.py <migration-name>
   ```

2. **Review Migration**
   Reference `references/migration_guide.md` for best practices:
   - Verify reversibility
   - Check for data loss risks
   - Validate naming conventions

3. **Test Migration**
   Use MCP tool `test_migration`:
   ```
   Use test_migration tool with migration file path
   ```

4. **Apply Migration**
   Use MCP tool `run_migration`:
   ```
   Use run_migration tool with migration file path
   ```

5. **Verify Schema**
   Use MCP tool `get_schema` and compare against expected state
```

**Use Cases:**
- Testing frameworks (tools + best practices)
- Deployment systems (tools + workflows)
- API clients (tools + usage patterns)

### Pattern 5: MCP + Slash Commands

**When to Use:**
- Tools with frequent shortcuts
- Quick access to tool functions
- User-friendly command interface

**Example: API Testing**
```
api-testing-plugin/
├── mcp-server/
│   └── src/
│       └── tools/
│           ├── sendRequest.ts
│           ├── validateResponse.ts
│           └── runTestSuite.ts
└── commands/
    ├── api-test.md
    ├── api-validate.md
    └── api-suite.md
```

**Command Integration:**
```markdown
# api-test.md

## Prompt

Quick API endpoint test: {{args}}

Expected format: METHOD /path [data]
Example: POST /users {"name":"John"}

Steps:
1. Parse method and path from args
2. Use MCP tool `send_request`:
   - method: parsed method
   - endpoint: parsed path
   - data: parsed data or empty
3. Display response status and body
4. Use MCP tool `validate_response` automatically
```

**Use Cases:**
- CLI-style tools
- Development utilities
- Quick operations on external services

### Pattern 6: Skill + Slash Commands

**When to Use:**
- Workflows with shortcuts
- Knowledge + quick actions
- No external integrations needed

**Example: Deployment Workflows**
```
deployment-plugin/
├── skill/
│   ├── SKILL.md
│   ├── references/
│   │   ├── deployment_checklist.md
│   │   ├── environments.md
│   │   └── rollback_procedures.md
│   └── scripts/
│       ├── deploy.sh
│       ├── rollback.sh
│       └── health_check.sh
└── commands/
    ├── deploy-dev.md
    ├── deploy-staging.md
    ├── deploy-prod.md
    └── rollback.md
```

**Integration:**
```markdown
# deploy-prod.md

## Prompt

Deploy to production using deployment skill.

⚠️ PRODUCTION DEPLOYMENT

Pre-deployment:
1. Load deployment skill
2. Reference `references/deployment_checklist.md`
3. Verify all checklist items

Deployment:
1. Run `scripts/deploy.sh production`
2. Monitor output for errors
3. Run `scripts/health_check.sh`

Post-deployment:
Reference `references/environments.md` for verification steps
```

**Use Cases:**
- Operational workflows
- Process automation
- Guided procedures

### Pattern 7: Full Plugin (MCP + Skill + Commands)

**When to Use:**
- Comprehensive solutions
- Complex domains
- Multiple interaction patterns needed

**Example: Testing Framework**
```
testing-framework/
├── mcp-server/
│   └── src/
│       ├── tools/
│       │   ├── runTests.ts
│       │   ├── getCoverage.ts
│       │   ├── generateReport.ts
│       │   └── mockService.ts
│       └── resources/
│           ├── testResults.ts
│           └── coverageData.ts
├── skill/
│   ├── SKILL.md
│   ├── references/
│   │   ├── testing_strategy.md
│   │   ├── best_practices.md
│   │   ├── mocking_patterns.md
│   │   └── coverage_guide.md
│   └── scripts/
│       ├── setup_tests.py
│       └── analyze_coverage.py
└── commands/
    ├── test-unit.md
    ├── test-integration.md
    ├── test-e2e.md
    ├── coverage.md
    └── test-watch.md
```

**Architecture Diagram:**
```
User Request
     ↓
Slash Commands (quick operations)
     ↓
Skill (workflow guidance + best practices)
     ↓
MCP Server (execute tests, gather data)
     ↓
Results + Analysis
```

**Component Interaction:**
```markdown
# SKILL.md

## Testing Workflow

### Quick Testing (via Commands)
- `/test-unit` - Run unit tests quickly
- `/test-integration` - Run integration tests
- `/test-e2e` - Run end-to-end tests

### Comprehensive Testing (via Skill)

1. **Planning**
   Reference `references/testing_strategy.md` for approach

2. **Setup**
   ```bash
   python scripts/setup_tests.py
   ```

3. **Execution**
   Use MCP tools:
   - `run_tests` with appropriate scope
   - `mock_service` for external dependencies

4. **Analysis**
   - Use `get_coverage` tool
   - Reference `references/coverage_guide.md`
   - Run `scripts/analyze_coverage.py`

5. **Reporting**
   Use `generate_report` tool
```

**Use Cases:**
- Development frameworks
- Complete workflows (deploy, test, monitor)
- Domain-specific environments

## Composition Patterns

### Pattern 8: Plugin Suite

**When to Use:**
- Related plugins working together
- Shared infrastructure
- Ecosystem of tools

**Example: Cloud Development Suite**
```
cloud-dev-suite/
├── infrastructure/
│   ├── aws-mcp-server/
│   ├── terraform-skill/
│   └── commands/
├── application/
│   ├── docker-mcp-server/
│   ├── kubernetes-skill/
│   └── commands/
└── monitoring/
    ├── metrics-mcp-server/
    ├── logging-skill/
    └── commands/
```

**Integration:**
```markdown
# Suite Configuration

Components work together:
- Infrastructure plugins create resources
- Application plugins deploy to infrastructure
- Monitoring plugins track application health

Shared configuration:
- AWS credentials
- Cluster endpoints
- Monitoring endpoints
```

### Pattern 9: Plugin Extension

**When to Use:**
- Extending existing plugins
- Adding domain-specific features
- Customizing for specific use case

**Example: Custom Test Framework Extension**
```
base-testing-framework/
└── [Standard testing plugin]

custom-api-testing/
├── mcp-server/
│   └── src/
│       └── tools/
│           ├── testGraphQL.ts    # New
│           └── testWebSocket.ts  # New
├── skill/
│   ├── SKILL.md                   # Extends base
│   └── references/
│       ├── graphql_testing.md     # New
│       └── websocket_testing.md   # New
└── commands/
    ├── test-graphql.md            # New
    └── test-websocket.md          # New
```

**Extension Pattern:**
```markdown
# Custom API Testing Skill

## Extending Base Testing Framework

This skill extends the base testing framework with:
- GraphQL endpoint testing
- WebSocket connection testing

### Usage with Base Framework

1. Use base framework for standard HTTP tests
2. Use this extension for GraphQL/WebSocket tests
3. Both use same reporting and coverage tools
```

## Scaling Patterns

### Pattern 10: Modular Architecture

**When to Use:**
- Large, complex plugins
- Team development
- Independent component evolution

**Structure:**
```
enterprise-plugin/
├── core/
│   ├── shared-types/
│   ├── shared-config/
│   └── shared-utils/
├── modules/
│   ├── auth-module/
│   │   ├── mcp-server/
│   │   ├── skill/
│   │   └── commands/
│   ├── data-module/
│   │   ├── mcp-server/
│   │   ├── skill/
│   │   └── commands/
│   └── deployment-module/
│       ├── mcp-server/
│       ├── skill/
│       └── commands/
└── integration/
    └── cross-module-workflows/
```

**Module Independence:**
```typescript
// Each module is self-contained
export class AuthModule {
  private mcp: AuthMCPServer;
  private skill: AuthSkill;
  private commands: AuthCommands;

  async initialize() {
    await this.mcp.start();
    this.skill.register();
    this.commands.register();
  }
}

// Modules can interact through defined interfaces
export interface ModuleInterface {
  initialize(): Promise<void>;
  cleanup(): Promise<void>;
  getTools(): Tool[];
  getSkills(): Skill[];
  getCommands(): Command[];
}
```

### Pattern 11: Plugin as Platform

**When to Use:**
- Extensible plugins
- Third-party extensions
- Plugin ecosystems

**Architecture:**
```
platform-plugin/
├── core/
│   ├── plugin-api/
│   ├── extension-loader/
│   └── registry/
├── built-in-extensions/
│   ├── basic-tools/
│   └── standard-workflows/
└── extension-interface/
    ├── types/
    ├── examples/
    └── documentation/
```

**Extension Interface:**
```typescript
// Extension developers implement this
export interface PluginExtension {
  name: string;
  version: string;
  dependencies?: string[];

  initialize(context: PluginContext): Promise<void>;

  getTools?(): Tool[];
  getSkills?(): Skill[];
  getCommands?(): Command[];
  getResources?(): Resource[];
}

// Platform provides context
export interface PluginContext {
  registerTool(tool: Tool): void;
  registerSkill(skill: Skill): void;
  registerCommand(command: Command): void;
  getSharedUtils(): Utils;
  getConfig(): Config;
}
```

## Integration Patterns

### Pattern 12: Multi-MCP Integration

**When to Use:**
- Multiple external services
- Service orchestration
- Complex integrations

**Example: Full-Stack Development Plugin**
```
fullstack-plugin/
├── skill/
│   ├── SKILL.md
│   └── references/
│       └── integration_patterns.md
└── commands/
    └── fullstack-deploy.md

# Uses existing MCP servers:
# - database MCP server
# - cloud MCP server
# - monitoring MCP server
```

**Orchestration Pattern:**
```markdown
# Deployment Workflow

Orchestrates multiple MCP servers:

1. **Database Setup** (database MCP)
   - Use `run_migration` tool
   - Use `seed_data` tool

2. **Application Deploy** (cloud MCP)
   - Use `deploy_service` tool
   - Use `configure_load_balancer` tool

3. **Monitoring Setup** (monitoring MCP)
   - Use `create_dashboard` tool
   - Use `setup_alerts` tool

4. **Verification**
   - Use `health_check` from cloud MCP
   - Use `get_metrics` from monitoring MCP
```

### Pattern 13: Progressive Enhancement

**When to Use:**
- Graceful degradation needed
- Optional features
- Environment-dependent functionality

**Pattern:**
```markdown
# Feature Detection Pattern

## Core Functionality (Always Available)
- Basic file operations
- Simple validations
- Essential commands

## Enhanced Functionality (Conditional)

### If Database MCP Available:
- Advanced query operations
- Transaction management
- Schema migrations

### If Cloud MCP Available:
- Cloud resource management
- Auto-scaling
- Global deployment

### If Both Available:
- Integrated cloud database solutions
- Automatic backups to cloud
- Cross-region replication
```

**Implementation:**
```typescript
class PluginFeatures {
  private availableFeatures: Set<string> = new Set();

  async detectFeatures() {
    if (await this.isDatabaseMCPAvailable()) {
      this.availableFeatures.add('database');
    }
    if (await this.isCloudMCPAvailable()) {
      this.availableFeatures.add('cloud');
    }
  }

  hasFeature(feature: string): boolean {
    return this.availableFeatures.has(feature);
  }

  async executeWithFallback<T>(
    preferredFn: () => Promise<T>,
    fallbackFn: () => Promise<T>
  ): Promise<T> {
    try {
      return await preferredFn();
    } catch (error) {
      console.warn('Falling back to basic implementation');
      return await fallbackFn();
    }
  }
}
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Monolithic Plugin

**Problem:**
```
mega-plugin/
└── everything/
    ├── 50+ tools
    ├── 20+ skills
    └── 100+ commands
```

**Solution:**
Break into focused plugins or use modular architecture.

### Anti-Pattern 2: Duplicated Logic

**Problem:**
```
plugin/
├── mcp-server/
│   └── src/validation.ts      # Same validation code
└── skill/
    └── scripts/validation.py  # Duplicated in Python
```

**Solution:**
Share logic through libraries or consolidate in one component.

### Anti-Pattern 3: Tight Coupling

**Problem:**
```typescript
// Skill hardcoded to specific MCP server version
if (mcpVersion !== '1.2.3') {
  throw new Error('Requires exact version 1.2.3');
}
```

**Solution:**
Use interfaces and version ranges:
```typescript
if (mcpVersion < '1.0.0' || mcpVersion >= '2.0.0') {
  throw new Error('Requires MCP server version ^1.0.0');
}
```

### Anti-Pattern 4: Poor Separation of Concerns

**Problem:**
```markdown
# Slash command doing too much
1. Business logic
2. Database operations
3. External API calls
4. File system operations
5. Complex calculations
```

**Solution:**
Commands delegate to skills/MCP:
```markdown
# Slash command orchestrates
1. Use skill for business logic and guidance
2. Use MCP tools for database and API operations
3. Use MCP tools for file operations
4. Report results
```

## Choosing the Right Pattern

### Decision Tree

```
Need external integration? ──No──> Pure Skill or Pure Commands
     │
    Yes
     │
     ├─> Simple integration ──> Pure MCP
     │
     └─> Complex workflows ──> MCP + Skill (+ Commands)

Need procedural knowledge? ──No──> Pure MCP or Pure Commands
     │
    Yes
     │
     ├─> Simple procedures ──> Pure Skill
     │
     └─> With tools ──> MCP + Skill

Need user shortcuts? ──No──> MCP and/or Skill
     │
    Yes
     │
     └─> Add Slash Commands
```

### Pattern Selection Matrix

| Requirements | Recommended Pattern |
|--------------|---------------------|
| API wrapper | Pure MCP |
| Best practices guide | Pure Skill |
| Quick shortcuts | Pure Commands |
| Tool + workflows | MCP + Skill |
| Tool + shortcuts | MCP + Commands |
| Workflows + shortcuts | Skill + Commands |
| Complete solution | Full Plugin |
| Related plugins | Plugin Suite |
| Extensible system | Plugin as Platform |

Following these architectural patterns ensures plugins are well-structured, maintainable, and scalable.
