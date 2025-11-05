# MCP Server Development Guide

Comprehensive guide for building Model Context Protocol (MCP) servers for Claude Code.

## What is an MCP Server?

An MCP server extends Claude's capabilities by providing:
- **Tools** - Functions Claude can call (like APIs)
- **Resources** - Data Claude can read (like databases)
- **Prompts** - Reusable prompt templates

MCP servers run as separate processes and communicate with Claude via standardized protocol.

## When to Create an MCP Server

Create an MCP server when you need:
- External service integration (databases, APIs, cloud services)
- Stateful operations (maintain connections, sessions, cache)
- Complex computations Claude shouldn't regenerate
- Real-time data access
- File system operations beyond Claude's native tools
- Custom tool combinations for specific workflows

## Language Selection

### TypeScript/Node.js

**Best for:**
- JavaScript/TypeScript ecosystem integration
- npm package utilization
- Web APIs and REST services
- JSON-heavy operations
- Real-time services (WebSocket, SSE)

**Pros:**
- Rich npm ecosystem
- Excellent async/await support
- Great for web services
- Easy JSON handling

**Cons:**
- Slower than compiled languages
- Higher memory usage
- Type safety requires TypeScript

### Python/FastMCP

**Best for:**
- Data science and ML integrations
- Scientific computing
- Python library ecosystem (pandas, numpy, etc.)
- File processing and transformations
- Database operations

**Pros:**
- Simpler syntax
- FastMCP makes MCP servers very easy
- Huge library ecosystem
- Great for data processing

**Cons:**
- Slower for I/O intensive tasks
- GIL limitations for concurrency
- Dependency management complexity

## MCP Server Architecture

### Core Components

```
mcp-server/
├── package.json / pyproject.toml    # Dependencies and metadata
├── src/ or app/                     # Source code
│   ├── index.ts / main.py          # Entry point
│   ├── tools/                       # Tool implementations
│   ├── resources/                   # Resource providers
│   └── config/                      # Configuration
├── tests/                           # Test suite
└── README.md                        # Documentation
```

### Tool Design

**Tool Definition:**
```typescript
// TypeScript
{
  name: "tool_name",
  description: "Clear description of what this tool does",
  inputSchema: {
    type: "object",
    properties: {
      param1: { type: "string", description: "Parameter description" },
      param2: { type: "number", description: "Parameter description" }
    },
    required: ["param1"]
  }
}
```

```python
# Python (FastMCP)
@mcp.tool()
def tool_name(param1: str, param2: int = 0) -> str:
    """Clear description of what this tool does"""
    # Implementation
    return result
```

**Tool Design Principles:**
1. **Single Responsibility** - Each tool does one thing well
2. **Clear Naming** - Tool name describes action (get_user, update_config)
3. **Comprehensive Description** - Explain what, why, and when to use
4. **Typed Parameters** - Strong typing with validation
5. **Error Handling** - Return meaningful errors, don't crash
6. **Idempotency** - Safe to call multiple times when possible

**Example - Good Tool Design:**
```typescript
{
  name: "search_database",
  description: "Search database records using SQL-like query syntax. Returns matching records with specified fields. Use this when you need to find specific data based on criteria.",
  inputSchema: {
    type: "object",
    properties: {
      table: {
        type: "string",
        description: "Table name to search in (users, orders, products)"
      },
      query: {
        type: "string",
        description: "Search criteria in SQL WHERE clause format"
      },
      fields: {
        type: "array",
        items: { type: "string" },
        description: "Fields to return. If empty, returns all fields."
      },
      limit: {
        type: "number",
        description: "Maximum records to return (default 100, max 1000)"
      }
    },
    required: ["table", "query"]
  }
}
```

### Resource Design

**Resource Definition:**
```typescript
// TypeScript
{
  uri: "resource://namespace/resource-id",
  name: "Human readable name",
  description: "What data this resource provides",
  mimeType: "application/json" // or text/plain, etc.
}
```

```python
# Python (FastMCP)
@mcp.resource("resource://namespace/resource-id")
def resource_name() -> str:
    """What data this resource provides"""
    return data
```

**Resource Design Principles:**
1. **Stable URIs** - Don't change resource URIs
2. **Structured Data** - Use JSON for complex data
3. **Documentation** - Explain data structure
4. **Efficient Access** - Cache when appropriate
5. **Versioning** - Include version in URI if schema changes

## Implementation Patterns

### Error Handling

**TypeScript:**
```typescript
async function handleToolCall(name: string, args: any) {
  try {
    // Validate inputs
    if (!args.param) {
      throw new Error("Missing required parameter: param");
    }

    // Execute operation
    const result = await performOperation(args);

    // Return success
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  } catch (error) {
    // Return error with context
    return {
      content: [{
        type: "text",
        text: `Error in ${name}: ${error.message}`
      }],
      isError: true
    };
  }
}
```

**Python (FastMCP):**
```python
@mcp.tool()
def perform_operation(param: str) -> str:
    """Perform an operation with proper error handling"""
    try:
        # Validate inputs
        if not param:
            raise ValueError("Missing required parameter: param")

        # Execute operation
        result = execute_operation(param)

        # Return success
        return json.dumps(result)
    except Exception as e:
        # Return error with context
        return f"Error in perform_operation: {str(e)}"
```

### State Management

**Connection Pooling:**
```typescript
class DatabaseServer {
  private pool: Pool;

  async initialize() {
    this.pool = createPool({
      host: config.host,
      database: config.database,
      max: 10 // Connection pool size
    });
  }

  async executeQuery(query: string) {
    const client = await this.pool.connect();
    try {
      return await client.query(query);
    } finally {
      client.release(); // Always release connections
    }
  }

  async cleanup() {
    await this.pool.end(); // Clean shutdown
  }
}
```

**Caching:**
```python
from functools import lru_cache
from datetime import datetime, timedelta

class APIClient:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = timedelta(minutes=5)

    def get_data(self, key: str) -> dict:
        # Check cache
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_ttl:
                return data

        # Fetch fresh data
        data = self._fetch_from_api(key)
        self.cache[key] = (data, datetime.now())
        return data
```

### Configuration Management

**Environment Variables:**
```typescript
// config.ts
import * as dotenv from 'dotenv';

dotenv.config();

export const config = {
  apiKey: process.env.API_KEY || throwRequired('API_KEY'),
  apiUrl: process.env.API_URL || 'https://api.example.com',
  timeout: parseInt(process.env.TIMEOUT || '30000'),
  debug: process.env.DEBUG === 'true'
};

function throwRequired(name: string): never {
  throw new Error(`Missing required environment variable: ${name}`);
}
```

**Python:**
```python
# config.py
import os
from typing import Optional

class Config:
    def __init__(self):
        self.api_key = self._get_required('API_KEY')
        self.api_url = os.getenv('API_URL', 'https://api.example.com')
        self.timeout = int(os.getenv('TIMEOUT', '30'))
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'

    def _get_required(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Missing required environment variable: {name}")
        return value

config = Config()
```

## Testing MCP Servers

### Unit Tests

**TypeScript (Jest):**
```typescript
describe('DatabaseTools', () => {
  let server: DatabaseServer;

  beforeEach(async () => {
    server = new DatabaseServer();
    await server.initialize();
  });

  afterEach(async () => {
    await server.cleanup();
  });

  test('search_database returns results', async () => {
    const result = await server.searchDatabase({
      table: 'users',
      query: 'name LIKE "John%"'
    });

    expect(result).toBeDefined();
    expect(Array.isArray(result.rows)).toBe(true);
  });

  test('search_database handles errors', async () => {
    await expect(
      server.searchDatabase({ table: 'invalid', query: '' })
    ).rejects.toThrow();
  });
});
```

**Python (pytest):**
```python
import pytest
from app.main import MCPServer

@pytest.fixture
def server():
    s = MCPServer()
    yield s
    s.cleanup()

def test_search_database_returns_results(server):
    result = server.search_database(
        table='users',
        query='name LIKE "John%"'
    )
    assert result is not None
    assert isinstance(result, list)

def test_search_database_handles_errors(server):
    with pytest.raises(ValueError):
        server.search_database(table='invalid', query='')
```

### Integration Tests

Test with actual Claude Code:
```bash
# Add server to Claude Code config
mcp add /path/to/server

# Test in Claude Code
"Use the search_database tool to find all users named John"
```

## Performance Optimization

### Async Operations

**TypeScript:**
```typescript
// Bad - Sequential
async function processItems(items: string[]) {
  const results = [];
  for (const item of items) {
    results.push(await processItem(item)); // Slow!
  }
  return results;
}

// Good - Parallel
async function processItems(items: string[]) {
  return Promise.all(items.map(item => processItem(item)));
}
```

**Python:**
```python
# Bad - Sequential
def process_items(items: list[str]) -> list:
    results = []
    for item in items:
        results.append(process_item(item))  # Slow!
    return results

# Good - Parallel with asyncio
import asyncio

async def process_items(items: list[str]) -> list:
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks)
```

### Lazy Loading

```typescript
class ResourceProvider {
  private cache: Map<string, any> = new Map();

  async getResource(uri: string) {
    // Load only when requested
    if (!this.cache.has(uri)) {
      this.cache.set(uri, await this.loadResource(uri));
    }
    return this.cache.get(uri);
  }
}
```

### Pagination

```typescript
interface PaginatedResult {
  data: any[];
  nextCursor?: string;
  hasMore: boolean;
}

async function searchWithPagination(
  query: string,
  cursor?: string,
  limit: number = 100
): Promise<PaginatedResult> {
  const results = await db.query(query, cursor, limit + 1);

  return {
    data: results.slice(0, limit),
    nextCursor: results.length > limit ? results[limit].id : undefined,
    hasMore: results.length > limit
  };
}
```

## Security Best Practices

### Input Validation

```typescript
import Joi from 'joi';

const querySchema = Joi.object({
  table: Joi.string().alphanum().required(),
  query: Joi.string().max(1000).required(),
  limit: Joi.number().integer().min(1).max(1000).default(100)
});

function validateInput(args: any) {
  const { error, value } = querySchema.validate(args);
  if (error) {
    throw new Error(`Invalid input: ${error.message}`);
  }
  return value;
}
```

### SQL Injection Prevention

```typescript
// Bad - SQL Injection vulnerable
function searchUsers(name: string) {
  return db.query(`SELECT * FROM users WHERE name = '${name}'`);
}

// Good - Parameterized queries
function searchUsers(name: string) {
  return db.query('SELECT * FROM users WHERE name = $1', [name]);
}
```

### Rate Limiting

```typescript
class RateLimiter {
  private requests = new Map<string, number[]>();

  async checkLimit(key: string, maxRequests: number, windowMs: number) {
    const now = Date.now();
    const requests = this.requests.get(key) || [];

    // Remove old requests
    const validRequests = requests.filter(time => now - time < windowMs);

    if (validRequests.length >= maxRequests) {
      throw new Error('Rate limit exceeded');
    }

    validRequests.push(now);
    this.requests.set(key, validRequests);
  }
}
```

## Deployment and Distribution

### Package Configuration

**TypeScript (package.json):**
```json
{
  "name": "mcp-server-myservice",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "mcp-server-myservice": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0"
  }
}
```

**Python (pyproject.toml):**
```toml
[project]
name = "mcp-server-myservice"
version = "1.0.0"
dependencies = [
    "mcp>=0.9.0"
]

[project.scripts]
mcp-server-myservice = "app.main:main"
```

### Installation Instructions

```markdown
# Installation

## TypeScript
npm install -g mcp-server-myservice

## Python
pip install mcp-server-myservice

# Configuration
Add to Claude Code config (~/.claude/config.json):
{
  "mcpServers": {
    "myservice": {
      "command": "mcp-server-myservice",
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

## Debugging MCP Servers

### Logging

**TypeScript:**
```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'mcp-server.log' })
  ]
});

logger.info('Tool called', { name: 'search_database', args });
```

**Python:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mcp-server.log'
)

logger = logging.getLogger(__name__)
logger.info(f'Tool called: {name} with args: {args}')
```

### Testing Locally

```bash
# Start server in debug mode
DEBUG=true npm start

# Or for Python
LOG_LEVEL=debug python -m app.main

# Test with curl (if server supports HTTP)
curl -X POST http://localhost:3000/tools/search_database \
  -H "Content-Type: application/json" \
  -d '{"table":"users","query":"name LIKE \"John%\""}'
```

## Common Patterns

### Database Integration
- Connection pooling
- Query builders
- Transaction management
- Migration tools

### API Integration
- Authentication handling
- Rate limiting
- Retry logic
- Response caching

### File Operations
- Stream processing
- Batch operations
- Format conversions
- Validation

### Real-time Services
- WebSocket connections
- Event subscriptions
- Message queuing
- State synchronization

## References

- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [TypeScript MCP SDK](https://github.com/modelcontextprotocol/typescript-sdk)
