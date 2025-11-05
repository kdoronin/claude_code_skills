# Plugin Development Best Practices

Comprehensive best practices for building high-quality Claude Code plugins.

## General Principles

### 1. Clear Purpose and Scope

**Single Responsibility**
- Each plugin should solve one problem well
- Avoid feature creep and scope expansion
- Focus on specific use case or domain

**Example:**
```
Good: "Database schema management plugin"
Bad: "Full-stack development plugin" (too broad)
```

**Clear Value Proposition**
- Explain what problem the plugin solves
- Define target users and use cases
- Demonstrate benefits over manual approaches

### 2. User-Centric Design

**Intuitive Activation**
- Clear triggers for skill activation
- Obvious command names
- Discoverable functionality

**Consistent UX**
- Uniform naming conventions
- Predictable behavior
- Similar patterns across components

**Progressive Disclosure**
- Essential info immediately available
- Details loaded as needed
- Advanced features don't clutter basics

## MCP Server Best Practices

### Tool Design

**Granular Tools**
```typescript
// Good - Focused tools
get_user(id: string)
update_user(id: string, data: UserData)
delete_user(id: string)

// Bad - Monolithic tool
manage_user(action: string, id?: string, data?: any)
```

**Type Safety**
```typescript
// Good - Strong typing
interface CreateUserInput {
  email: string;
  name: string;
  role: 'admin' | 'user' | 'guest';
}

function createUser(input: CreateUserInput): User

// Bad - Weak typing
function createUser(data: any): any
```

**Comprehensive Descriptions**
```typescript
{
  name: "search_users",
  description: "Search users by name, email, or role. Returns paginated results sorted by relevance. Use this when you need to find users matching specific criteria or list users with filters.",
  // vs
  description: "Search users" // Too brief
}
```

### Error Handling

**Detailed Error Messages**
```typescript
// Good
throw new Error(
  `Failed to connect to database: ${error.message}. ` +
  `Check that DATABASE_URL is set and database is running.`
);

// Bad
throw new Error("Database error");
```

**Graceful Degradation**
```typescript
async function getUserWithCache(id: string) {
  try {
    // Try cache first
    return await cache.get(id);
  } catch (cacheError) {
    console.warn("Cache miss, fetching from database");
    // Fallback to database
    return await db.getUser(id);
  }
}
```

**Error Recovery**
```typescript
async function executeWithRetry<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(Math.pow(2, i) * 1000); // Exponential backoff
    }
  }
  throw new Error("Unreachable");
}
```

### Performance

**Connection Pooling**
```typescript
// Good - Reuse connections
const pool = new Pool({ max: 10 });

async function query(sql: string) {
  const client = await pool.connect();
  try {
    return await client.query(sql);
  } finally {
    client.release();
  }
}

// Bad - Create connection per request
async function query(sql: string) {
  const client = new Client();
  await client.connect();
  const result = await client.query(sql);
  await client.end();
  return result;
}
```

**Caching Strategy**
```typescript
class CacheManager {
  private cache = new Map<string, { data: any; expiry: number }>();

  set(key: string, data: any, ttlMs: number) {
    this.cache.set(key, {
      data,
      expiry: Date.now() + ttlMs
    });
  }

  get(key: string): any | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() > entry.expiry) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  // Cleanup expired entries periodically
  startCleanup(intervalMs: number = 60000) {
    setInterval(() => {
      const now = Date.now();
      for (const [key, entry] of this.cache) {
        if (now > entry.expiry) {
          this.cache.delete(key);
        }
      }
    }, intervalMs);
  }
}
```

**Pagination**
```typescript
interface PaginationOptions {
  limit: number;
  cursor?: string;
}

interface PaginatedResponse<T> {
  data: T[];
  nextCursor?: string;
  hasMore: boolean;
}

async function getUsers(
  options: PaginationOptions
): Promise<PaginatedResponse<User>> {
  const { limit, cursor } = options;

  // Fetch limit + 1 to determine if more exist
  const users = await db.query(
    'SELECT * FROM users WHERE id > $1 ORDER BY id LIMIT $2',
    [cursor || '0', limit + 1]
  );

  const hasMore = users.length > limit;
  const data = users.slice(0, limit);

  return {
    data,
    nextCursor: hasMore ? data[data.length - 1].id : undefined,
    hasMore
  };
}
```

### Security

**Input Validation**
```typescript
import Joi from 'joi';

const userSchema = Joi.object({
  email: Joi.string().email().required(),
  name: Joi.string().min(2).max(100).required(),
  age: Joi.number().integer().min(0).max(150)
});

function validateUser(data: any): User {
  const { error, value } = userSchema.validate(data);
  if (error) {
    throw new Error(`Invalid user data: ${error.message}`);
  }
  return value;
}
```

**SQL Injection Prevention**
```typescript
// Good - Parameterized query
db.query('SELECT * FROM users WHERE email = $1', [email]);

// Bad - String interpolation
db.query(`SELECT * FROM users WHERE email = '${email}'`);
```

**Rate Limiting**
```typescript
class RateLimiter {
  private requests = new Map<string, number[]>();

  async checkLimit(
    key: string,
    maxRequests: number,
    windowMs: number
  ): Promise<void> {
    const now = Date.now();
    const requests = this.requests.get(key) || [];

    // Remove old requests outside window
    const validRequests = requests.filter(
      time => now - time < windowMs
    );

    if (validRequests.length >= maxRequests) {
      const oldestRequest = Math.min(...validRequests);
      const retryAfter = windowMs - (now - oldestRequest);
      throw new Error(
        `Rate limit exceeded. Retry after ${retryAfter}ms`
      );
    }

    validRequests.push(now);
    this.requests.set(key, validRequests);
  }
}
```

**Environment Variables**
```typescript
// Good - Validate at startup
function getConfig() {
  const apiKey = process.env.API_KEY;
  if (!apiKey) {
    throw new Error('API_KEY environment variable is required');
  }

  return {
    apiKey,
    apiUrl: process.env.API_URL || 'https://api.default.com',
    timeout: parseInt(process.env.TIMEOUT || '30000')
  };
}

const config = getConfig(); // Fail fast if misconfigured
```

## Skill Best Practices

### Documentation Quality

**Clear Triggers**
```markdown
Good:
## When to Use This Skill

Use this skill when:
- Testing REST API endpoints
- Validating API responses
- Creating API test suites
- Debugging API integration

Bad:
## When to Use
Use for API stuff.
```

**Concrete Examples**
```markdown
Good:
### Example: User Authentication

Test the login endpoint:
```bash
python scripts/api_test.py \
  --endpoint /auth/login \
  --method POST \
  --data '{"email":"user@example.com","password":"pass123"}'
```

Expected response:
```json
{
  "token": "eyJ...",
  "user": { "id": "123", "email": "user@example.com" }
}
```

Bad:
### Example
Run the test script with appropriate parameters.
```

### Resource Organization

**Logical Structure**
```
Good:
skill-name/
├── SKILL.md
├── scripts/
│   ├── test.py
│   ├── validate.py
│   └── utils.py
├── references/
│   ├── api_schema.md
│   ├── examples.md
│   └── troubleshooting.md
└── assets/
    └── templates/
        ├── request.json
        └── test-suite/

Bad:
skill-name/
├── SKILL.md
├── everything/
│   ├── script1.py
│   ├── doc.md
│   ├── template.json
│   └── other_stuff/
```

**Size Management**
```markdown
Good:
# Large Reference Files

For API schema, use grep to find specific endpoints:
```bash
grep -A 20 "POST /auth/login" references/api_schema.md
```

Common endpoints:
- Authentication: /auth/*
- Users: /users/*
- Orders: /orders/*

Bad:
[Dumping entire 10,000 line API spec into SKILL.md]
```

### Script Quality

**CLI Interface**
```python
# Good
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Test API endpoints"
    )
    parser.add_argument('endpoint', help='API endpoint path')
    parser.add_argument('--method', default='GET',
                       choices=['GET', 'POST', 'PUT', 'DELETE'])
    parser.add_argument('--data', help='Request body JSON')
    parser.add_argument('--auth-token', help='Auth token')

    args = parser.parse_args()
    # Execute with parsed args

# Bad
import sys
endpoint = sys.argv[1] if len(sys.argv) > 1 else None
method = sys.argv[2] if len(sys.argv) > 2 else 'GET'
# No validation, no help text, fragile
```

**Error Handling in Scripts**
```python
# Good
import sys

def run_test(endpoint: str) -> int:
    try:
        result = execute_test(endpoint)
        print(f"✓ Test passed: {result}")
        return 0
    except ValidationError as e:
        print(f"✗ Validation failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(run_test(sys.argv[1]))

# Bad
def run_test(endpoint):
    result = execute_test(endpoint)  # May crash
    print(result)

run_test(sys.argv[1])  # No exit codes
```

## Slash Command Best Practices

### Command Naming

**Descriptive Names**
```
Good:
/deploy:prod
/test:integration
/db:migrate
/format:code

Bad:
/d
/t
/m
/f
```

**Consistent Namespacing**
```
Good:
/api:test
/api:validate
/api:mock

/db:migrate
/db:seed
/db:rollback

Bad:
/test-api
/validateApi
/mock_api_response
```

### Argument Handling

**Clear Expectations**
```markdown
Good:
## Prompt

Deploy to {{args}} environment.

Expected: dev, staging, or prod

If no argument:
  Display: "Usage: /deploy <environment>"
  Do not proceed

If invalid environment:
  Display: "Invalid environment. Use: dev, staging, or prod"
  Do not proceed

Bad:
## Prompt
Deploy {{args}}
[No validation or guidance]
```

### User Feedback

**Progress Indication**
```markdown
Good:
## Prompt

Deploying to {{args}}...

1. ✓ Running tests
2. ✓ Building production bundle
3. → Uploading to server
4. ⏳ Restarting services
5. ⏳ Running health checks

Bad:
## Prompt
Deploying... [Long wait with no feedback]
```

## Testing Best Practices

### Automated Testing

**MCP Server Tests**
```typescript
describe('MCP Server', () => {
  let server: MCPServer;

  beforeAll(async () => {
    server = new MCPServer();
    await server.initialize();
  });

  afterAll(async () => {
    await server.cleanup();
  });

  describe('search_users tool', () => {
    it('returns users matching query', async () => {
      const result = await server.tools.search_users({
        query: 'john',
        limit: 10
      });

      expect(result.data).toHaveLength(expect.any(Number));
      expect(result.data[0]).toHaveProperty('email');
    });

    it('handles pagination correctly', async () => {
      const page1 = await server.tools.search_users({
        query: 'test',
        limit: 5
      });

      expect(page1.data).toHaveLength(5);
      expect(page1.hasMore).toBe(true);

      const page2 = await server.tools.search_users({
        query: 'test',
        limit: 5,
        cursor: page1.nextCursor
      });

      expect(page2.data[0].id).not.toBe(page1.data[0].id);
    });

    it('validates input parameters', async () => {
      await expect(
        server.tools.search_users({ query: '', limit: 0 })
      ).rejects.toThrow('Invalid parameters');
    });
  });
});
```

### Manual Testing

**Test Checklist**
```
MCP Server:
□ All tools execute successfully
□ Error messages are clear
□ Resources load correctly
□ Configuration works
□ Cleanup happens properly

Skill:
□ Triggers appropriately
□ Workflows are complete
□ Scripts execute
□ References load
□ Assets accessible
□ Examples work

Slash Commands:
□ Commands trigger
□ Arguments parse correctly
□ Integration works
□ Errors are handled
□ Output is clear
```

## Documentation Best Practices

### README Structure

```markdown
# Plugin Name

Brief description of what the plugin does and why it's useful.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

### Prerequisites
- Requirement 1
- Requirement 2

### Install Steps
```bash
# Installation commands
```

### Configuration
```json
{
  "config": "example"
}
```

## Usage

### Quick Start
[Simple example to get started]

### Common Operations
[Frequent use cases]

### Advanced Usage
[Complex scenarios]

## Components

### MCP Server (if applicable)
- Tool 1: Description
- Tool 2: Description

### Skills (if applicable)
- Skill purpose and workflows

### Commands (if applicable)
- Command list and usage

## Troubleshooting

Common issues and solutions.

## Development

How to contribute or modify.

## License

[License information]
```

### API Documentation

**Tool Documentation**
```typescript
/**
 * Search for users matching query criteria.
 *
 * @param query - Search string to match against name or email
 * @param limit - Maximum results to return (default: 100, max: 1000)
 * @param cursor - Pagination cursor from previous response
 * @returns Paginated user results with next cursor
 *
 * @example
 * ```typescript
 * const users = await searchUsers({
 *   query: 'john',
 *   limit: 10
 * });
 * ```
 *
 * @throws {ValidationError} If query is empty or limit is invalid
 * @throws {DatabaseError} If database connection fails
 */
async function searchUsers(
  query: string,
  limit?: number,
  cursor?: string
): Promise<PaginatedResponse<User>>
```

## Performance Best Practices

### Optimization Strategies

**Lazy Loading**
```typescript
class PluginManager {
  private plugins = new Map<string, Plugin>();

  async getPlugin(name: string): Promise<Plugin> {
    // Load only when needed
    if (!this.plugins.has(name)) {
      this.plugins.set(name, await this.loadPlugin(name));
    }
    return this.plugins.get(name)!;
  }
}
```

**Batch Operations**
```typescript
// Good - Batch multiple operations
async function updateUsers(users: User[]) {
  await db.batchUpdate(users); // Single transaction
}

// Bad - Individual operations
async function updateUsers(users: User[]) {
  for (const user of users) {
    await db.update(user); // Many transactions
  }
}
```

**Parallel Execution**
```typescript
// Good - Parallel independent operations
const [users, orders, products] = await Promise.all([
  fetchUsers(),
  fetchOrders(),
  fetchProducts()
]);

// Bad - Sequential when unnecessary
const users = await fetchUsers();
const orders = await fetchOrders();
const products = await fetchProducts();
```

## Maintenance Best Practices

### Versioning

**Semantic Versioning**
```
1.0.0 - Initial release
1.0.1 - Bug fixes
1.1.0 - New features (backward compatible)
2.0.0 - Breaking changes
```

**Changelog**
```markdown
# Changelog

## [2.0.0] - 2024-01-15
### Breaking Changes
- Renamed tool `get_user` to `fetch_user`
- Changed response format for `search_users`

### Added
- New tool: `batch_update_users`
- Pagination support for all list operations

### Fixed
- Connection leak in database pool
- Race condition in cache invalidation

## [1.1.0] - 2023-12-01
### Added
- Caching layer for improved performance
- Rate limiting support
```

### Deprecation

**Graceful Deprecation**
```typescript
/**
 * @deprecated Use fetchUser instead. Will be removed in v3.0.0
 */
function getUser(id: string): Promise<User> {
  console.warn(
    'getUser is deprecated. Use fetchUser instead.'
  );
  return fetchUser(id);
}
```

## Security Best Practices Summary

1. **Validate All Inputs** - Never trust external data
2. **Use Parameterized Queries** - Prevent injection attacks
3. **Secure Configuration** - Environment variables, not hardcoded
4. **Rate Limiting** - Prevent abuse
5. **Error Messages** - Don't leak sensitive info
6. **Dependency Updates** - Keep dependencies current
7. **Least Privilege** - Minimal permissions needed
8. **Audit Logging** - Track security-relevant actions

## Quality Checklist

Before releasing a plugin:

**Functionality**
- [ ] All features work as documented
- [ ] Error handling is comprehensive
- [ ] Edge cases are handled
- [ ] Performance is acceptable

**Documentation**
- [ ] README is complete and clear
- [ ] All components documented
- [ ] Examples are accurate
- [ ] Troubleshooting guide included

**Testing**
- [ ] Automated tests pass
- [ ] Manual testing completed
- [ ] Integration testing done
- [ ] Security review performed

**Code Quality**
- [ ] Code is well-organized
- [ ] Naming is consistent
- [ ] No code duplication
- [ ] Comments explain why, not what

**Distribution**
- [ ] Version number set
- [ ] Changelog updated
- [ ] Dependencies specified
- [ ] Installation tested

Following these best practices ensures plugins are reliable, maintainable, and user-friendly.
