# Skill Development Guide

Comprehensive guide for creating effective skills for Claude Code.

## What is a Skill?

A skill is a modular package that provides Claude with:
- **Specialized knowledge** - Domain expertise and procedural workflows
- **Bundled resources** - Scripts, references, and assets
- **Tool integration guidance** - How to use specific tools effectively

Skills act as "onboarding guides" that transform Claude from general-purpose to specialized agent.

## When to Create a Skill

Create a skill when you need:
- Procedural workflows for specific domains
- Domain-specific knowledge that Claude doesn't possess
- Reusable scripts and tools bundled together
- Company-specific processes and standards
- Multi-step procedures that are repeatedly executed
- Integration patterns for specific tools or frameworks

## Skill Anatomy

### Required Components

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
```

### Optional Bundled Resources

```
skill-name/
├── SKILL.md
├── scripts/ (optional)
│   └── *.py, *.sh, *.js - Executable code
├── references/ (optional)
│   └── *.md - Documentation loaded as needed
└── assets/ (optional)
    └── * - Files used in output
```

## SKILL.md Structure

### YAML Frontmatter

**Required metadata:**
```yaml
---
name: skill-name
description: Clear description of what skill does and when to use it. This should be specific enough that Claude knows when to activate this skill. Use third person (e.g., "This skill should be used when..." not "Use this skill when...").
---
```

**Best Practices:**
- **Name:** lowercase-with-dashes, descriptive, unique
- **Description:** 1-3 sentences, specific triggers, clear purpose
- **Third person:** Always use third person in description

**Good Examples:**
```yaml
---
name: api-testing
description: This skill provides workflows and tools for testing REST APIs. It should be used when testing API endpoints, validating responses, or creating API test suites.
---
```

**Bad Examples:**
```yaml
---
name: testing
description: For testing stuff
---
```

### Markdown Instructions

**Structure:**
1. **Purpose** - What problem does this skill solve?
2. **When to Use** - Specific triggers and use cases
3. **Workflows** - Step-by-step procedures
4. **Resources** - How to use bundled scripts/references/assets
5. **Examples** - Concrete usage examples

**Writing Style:**
- Use imperative/infinitive form (verb-first)
- Objective, instructional language
- Not second person - avoid "you should"
- Example: "To accomplish X, do Y" not "You should do X"

**Template:**
```markdown
---
name: skill-name
description: [Clear, specific description]
---

# Skill Name

## Purpose

[What problem does this solve? 2-3 sentences]

## When to Use This Skill

Use this skill when:
- [Specific trigger 1]
- [Specific trigger 2]
- [Specific trigger 3]

## Workflows

### [Workflow Name 1]

[Step-by-step procedure]

1. [Step 1]
2. [Step 2]
3. [Step 3]

### [Workflow Name 2]

[Another procedure]

## Using Bundled Resources

### Scripts

[How to use scripts in scripts/]

### References

[When to load references from references/]

### Assets

[How to use assets from assets/]

## Examples

### Example 1: [Use Case]

[Concrete example with commands/steps]

### Example 2: [Use Case]

[Another concrete example]
```

## Bundled Resources

### Scripts Directory (`scripts/`)

**Purpose:** Executable code for deterministic operations

**When to Include:**
- Code is repeatedly rewritten
- Deterministic reliability needed
- Complex operations better handled by code
- Token efficiency desired

**Best Practices:**
- One script per focused task
- Clear command-line interfaces
- Proper error handling
- Documentation in script headers
- Executable permissions set

**Example Script Structure:**
```python
#!/usr/bin/env python3
"""
Script: rotate_pdf.py
Purpose: Rotate PDF pages by specified degrees
Usage: python rotate_pdf.py <input.pdf> <output.pdf> --degrees 90
"""

import argparse
import sys
from typing import Optional

def rotate_pdf(input_path: str, output_path: str, degrees: int) -> None:
    """Rotate PDF pages by specified degrees."""
    try:
        # Implementation
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Rotate PDF pages")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("output", help="Output PDF file")
    parser.add_argument("--degrees", type=int, default=90,
                       choices=[90, 180, 270],
                       help="Rotation degrees")

    args = parser.parse_args()
    rotate_pdf(args.input, args.output, args.degrees)

if __name__ == "__main__":
    main()
```

**Referencing in SKILL.md:**
```markdown
## Using PDF Rotation

To rotate a PDF, use the bundled script:

```bash
python scripts/rotate_pdf.py input.pdf output.pdf --degrees 90
```

The script supports rotation by 90, 180, or 270 degrees.
```

### References Directory (`references/`)

**Purpose:** Documentation loaded into context as needed

**When to Include:**
- Detailed schemas and specifications
- API documentation
- Domain knowledge references
- Workflow guides
- Company policies and standards
- Examples and templates

**Best Practices:**
- Break into focused files (not monolithic)
- Use descriptive filenames
- Include grep patterns for large files
- Avoid duplication with SKILL.md
- Use markdown for formatting

**Example References:**
```
references/
├── api_schema.md           # API endpoint specifications
├── database_schema.md      # Database table structures
├── deployment_guide.md     # Detailed deployment procedures
├── error_codes.md          # Error code reference
└── examples.md             # Usage examples and patterns
```

**File Structure:**
```markdown
# API Schema Reference

## Authentication Endpoints

### POST /auth/login

Request:
```json
{
  "email": "string",
  "password": "string"
}
```

Response:
```json
{
  "token": "string",
  "user": {
    "id": "string",
    "email": "string"
  }
}
```

## User Endpoints

[Additional endpoints...]
```

**Referencing in SKILL.md:**
```markdown
## API Integration

For detailed API specifications, reference `references/api_schema.md`.

When working with authentication:
```bash
# Load API schema reference
Read references/api_schema.md

# Or grep for specific endpoint
grep -A 20 "POST /auth/login" references/api_schema.md
```
```

**Large File Patterns:**
```markdown
## Database Schema

The complete database schema is in `references/database_schema.md`.

To find specific table:
```bash
grep -A 10 "Table: users" references/database_schema.md
```

Common tables:
- `users` - User accounts and profiles
- `orders` - Order transactions
- `products` - Product catalog
```

### Assets Directory (`assets/`)

**Purpose:** Files used in output, not loaded into context

**When to Include:**
- Templates for output files
- Images, icons, logos
- Boilerplate code
- Fonts and styles
- Sample documents

**Best Practices:**
- Organize by type or purpose
- Use clear naming
- Include usage instructions in SKILL.md
- Keep files optimized (compress images)
- Version control friendly formats

**Example Assets:**
```
assets/
├── templates/
│   ├── html-boilerplate/
│   ├── react-component/
│   └── api-client/
├── images/
│   ├── logo.png
│   └── icons/
└── fonts/
    └── custom-font.ttf
```

**Usage in Workflows:**
```markdown
## Creating New Component

To create a new React component, copy the template:

```bash
cp -r assets/templates/react-component/ src/components/NewComponent
```

Then customize:
1. Rename files to match component name
2. Update component logic
3. Add to exports
```

## Progressive Disclosure

Skills use three-level loading:

### Level 1: Metadata (Always in Context)
- Skill name
- Description
- ~100 words
- Determines when skill loads

### Level 2: SKILL.md Body (When Skill Triggers)
- Main instructions
- Workflows
- Resource references
- <5k words ideal

### Level 3: Bundled Resources (As Needed)
- Scripts (can execute without reading)
- References (load when needed)
- Assets (use without loading)
- Unlimited size

**Design Principle:**
Keep SKILL.md lean by moving details to references. Only include essential procedural knowledge in SKILL.md.

## Skill Triggers

### Explicit Triggers
- User invokes skill by name: "Use the api-testing skill"
- File patterns: Working with specific file types
- Keywords: Domain-specific terms

### Implicit Triggers
- Task patterns matching skill workflows
- Domain context (API testing, deployment, etc.)
- Tool usage patterns

### Best Trigger Design

**In Description:**
```yaml
description: This skill provides API testing workflows using REST clients and validation tools. Use when testing API endpoints, validating responses, creating test suites, or debugging API integration issues.
```

**In SKILL.md:**
```markdown
## When to Use This Skill

Use this skill when:
- Testing REST API endpoints
- Validating API responses
- Creating automated API test suites
- Debugging API integration issues
- Documenting API behavior
- Setting up API monitoring
```

## Workflow Design

### Good Workflow Structure

```markdown
### API Endpoint Testing Workflow

1. **Identify Endpoint**
   - Review API documentation in `references/api_schema.md`
   - Note endpoint URL, method, parameters

2. **Prepare Request**
   - Set authentication headers
   - Prepare request body if needed
   - Use `assets/templates/api-request.json` as template

3. **Execute Request**
   ```bash
   python scripts/api_test.py --endpoint /users --method GET
   ```

4. **Validate Response**
   - Check status code (200, 201, etc.)
   - Validate response schema
   - Use `scripts/validate_response.py` for schema validation

5. **Document Results**
   - Record response examples
   - Note any issues or edge cases
   - Update test suite if needed
```

### Multi-Path Workflows

```markdown
### Deployment Workflow

#### Production Deployment
1. Run full test suite
2. Create production build
3. Backup current production
4. Deploy to production
5. Verify deployment
6. Monitor for issues

#### Staging Deployment
1. Run smoke tests
2. Create staging build
3. Deploy to staging
4. Run integration tests

#### Emergency Hotfix
1. Create hotfix branch
2. Minimal testing
3. Direct production deployment
4. Post-deployment verification
```

## Examples and Use Cases

### Example 1: API Testing Skill

```markdown
---
name: api-testing
description: Provides workflows for testing REST APIs including request execution, response validation, and test suite management. Use when testing API endpoints, validating API responses, or creating API test automation.
---

# API Testing Skill

## Purpose

This skill provides comprehensive workflows for REST API testing, including
endpoint testing, response validation, and automated test suite creation.

## When to Use This Skill

Use this skill when:
- Testing REST API endpoints during development
- Validating API response formats and data
- Creating automated API test suites
- Debugging API integration issues
- Documenting API behavior

## Workflows

### Quick Endpoint Test

1. Use the test script:
   ```bash
   python scripts/api_test.py \\
     --endpoint /api/users \\
     --method GET \\
     --auth-token $TOKEN
   ```

2. Review response for status and data

### Response Schema Validation

1. Load expected schema from `references/api_schema.md`
2. Execute request
3. Validate with script:
   ```bash
   python scripts/validate_response.py \\
     --response response.json \\
     --schema references/schemas/user_response.json
   ```

## Using Bundled Resources

### Scripts
- `api_test.py` - Execute API requests with authentication
- `validate_response.py` - Validate responses against schemas
- `generate_tests.py` - Generate test suite from OpenAPI spec

### References
- `api_schema.md` - Complete API documentation
- `auth_guide.md` - Authentication patterns
- `error_codes.md` - API error code reference

### Assets
- `templates/test-suite/` - Test suite template
- `templates/api-request.json` - Request template

## Examples

### Example: Testing User Login

```bash
# Test login endpoint
python scripts/api_test.py \\
  --endpoint /auth/login \\
  --method POST \\
  --data '{"email":"test@example.com","password":"test123"}'

# Validate response
python scripts/validate_response.py \\
  --response last_response.json \\
  --schema references/schemas/auth_response.json
```
```

### Example 2: Code Review Skill

```markdown
---
name: code-review
description: Provides code review guidelines and checklists for systematic code quality assessment. Use when reviewing pull requests, conducting code audits, or establishing code review standards.
---

# Code Review Skill

## Purpose

This skill provides systematic code review workflows following industry
best practices and company standards.

## When to Use This Skill

Use this skill when:
- Reviewing pull requests
- Conducting code quality audits
- Establishing review standards
- Mentoring developers on code quality

## Workflows

### Standard PR Review

1. **Context Review**
   - Read PR description and linked issues
   - Review `references/review_checklist.md` for relevant items

2. **Code Analysis**
   - Check code organization and structure
   - Verify naming conventions
   - Review error handling
   - Assess test coverage

3. **Security Review**
   - Reference `references/security_checklist.md`
   - Check for common vulnerabilities
   - Validate input sanitization

4. **Documentation**
   - Add review comments
   - Use `assets/templates/review-comment.md` for structured feedback

## References

### Review Guidelines
Load `references/review_checklist.md` for comprehensive checklist covering:
- Code organization
- Naming conventions
- Error handling
- Testing
- Documentation
- Security
- Performance

### Security Checklist
Reference `references/security_checklist.md` for:
- Input validation
- Authentication/authorization
- Data exposure
- Injection vulnerabilities

## Examples

### Example: Security-Focused Review

```bash
# Load security checklist
Read references/security_checklist.md

# Review for SQL injection
grep -r "query.*\${" src/

# Review for XSS
grep -r "innerHTML\|dangerouslySetInnerHTML" src/
```
```

## Testing Skills

### Manual Testing

1. Install skill in Claude Code
2. Trigger skill with realistic requests
3. Verify workflows execute correctly
4. Check resource loading works
5. Validate output quality

### Testing Checklist

- [ ] Metadata is clear and accurate
- [ ] Description triggers appropriately
- [ ] Workflows are complete and correct
- [ ] Scripts execute without errors
- [ ] References load properly
- [ ] Assets are accessible
- [ ] Examples work as documented
- [ ] No broken references or paths

## Validation

Before packaging, validate:

```bash
# Check frontmatter format
head -10 SKILL.md

# Verify scripts are executable
ls -l scripts/

# Check for broken references
grep -r "references/" SKILL.md
grep -r "scripts/" SKILL.md
grep -r "assets/" SKILL.md

# Verify all referenced files exist
# [List should match actual files]
```

## Common Patterns

### Integration Skill
Combines MCP server usage with procedural knowledge:
```markdown
## Using the Database MCP Server

This skill works with the database MCP server.

### Query Workflow
1. Use `connect_db` tool to establish connection
2. Reference `references/schema.md` for table structure
3. Use `execute_query` tool with parameterized queries
4. Validate results
```

### Documentation Skill
Provides templates and standards:
```markdown
## API Documentation

Use the OpenAPI template:
```bash
cp assets/templates/openapi.yaml docs/api.yaml
```

Follow the documentation standards in `references/doc_standards.md`.
```

### Automation Skill
Bundles scripts for common tasks:
```markdown
## Build Automation

Run the build pipeline:
```bash
./scripts/build.sh --environment production
```

For custom builds, reference `references/build_options.md`.
```

## Best Practices Summary

1. **Clear Triggers** - Specific description and use cases
2. **Lean SKILL.md** - Move details to references
3. **Working Examples** - Concrete, tested examples
4. **Progressive Disclosure** - Right information at right time
5. **Resource Organization** - Logical structure
6. **Documentation** - Clear instructions for all components
7. **Testing** - Validate before packaging
8. **Maintenance** - Keep updated with changes
