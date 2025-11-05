# Skill Template

Template for creating Claude Code skills with best practices built-in.

## Quick Start

1. **Copy this template**
   ```bash
   cp -r skill-template/ my-new-skill/
   cd my-new-skill/
   ```

2. **Customize SKILL.md**
   - Update YAML frontmatter (name and description)
   - Replace template sections with your content
   - Add your workflows and examples

3. **Add bundled resources** (optional)
   - Add scripts to `scripts/`
   - Add references to `references/`
   - Add assets to `assets/`

4. **Test your skill**
   - Install in Claude Code skills directory
   - Test with realistic scenarios
   - Verify all examples work

5. **Package for distribution**
   ```bash
   # Create skill package
   zip -r my-skill.zip .
   ```

## Structure

```
skill-template/
├── SKILL.md                    # Main skill definition (required)
├── scripts/                    # Executable helper scripts (optional)
│   └── example_script.py       # Example script
├── references/                 # Reference documentation (optional)
│   └── example_reference.md    # Example reference
├── assets/                     # Files used in output (optional)
│   └── templates/              # Template files
└── README.md                   # This file
```

## Customization Checklist

- [ ] Update `name` in YAML frontmatter
- [ ] Update `description` in YAML frontmatter
- [ ] Replace purpose section
- [ ] Add specific trigger conditions
- [ ] Add your workflows with steps
- [ ] Add concrete examples
- [ ] Add scripts if needed
- [ ] Add reference documents if needed
- [ ] Add asset templates if needed
- [ ] Test all examples work
- [ ] Remove example files you don't need

## Best Practices

### Frontmatter
- Use lowercase-with-dashes for skill name
- Write specific, clear description
- Use third person ("This skill should be used...")

### Workflows
- Use step-by-step format
- Include concrete examples
- Reference bundled resources where appropriate
- Show expected outcomes

### Bundled Resources
- **Scripts:** For code that would be rewritten repeatedly
- **References:** For detailed docs loaded as needed
- **Assets:** For files used in output

### Examples
- Use real, working examples
- Include expected outputs
- Cover common use cases
- Show error handling

## Example Transformation

**Before (Template):**
```markdown
---
name: skill-template
description: Template for creating Claude Code skills...
---
```

**After (Your Skill):**
```markdown
---
name: api-testing
description: Provides workflows for testing REST APIs including request execution, response validation, and test suite management. Use when testing API endpoints or creating API test automation.
---

# API Testing Skill

## Purpose

This skill provides comprehensive workflows for REST API testing...
```

## Resources

- [Skill Guide](../../references/skill_guide.md)
- [Best Practices](../../references/best_practices.md)
- [Architecture Patterns](../../references/architecture_patterns.md)
