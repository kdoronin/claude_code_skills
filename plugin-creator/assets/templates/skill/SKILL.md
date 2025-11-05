---
name: skill-template
description: Template for creating Claude Code skills. Replace this description with a clear explanation of what this skill does and when it should be used. Be specific about triggers and use cases.
---

# Skill Template

Replace this section with a brief overview of your skill's purpose.

## Purpose

Explain what problem this skill solves and what value it provides.
Keep this to 2-3 sentences.

## When to Use This Skill

Use this skill when:
- [Specific trigger or use case 1]
- [Specific trigger or use case 2]
- [Specific trigger or use case 3]
- [Add more as needed]

## Workflows

### [Workflow Name 1]

[Description of this workflow and when to use it]

**Steps:**

1. **[Step Name]**
   [Step details and instructions]

2. **[Step Name]**
   [Step details and instructions]

3. **[Step Name]**
   [Step details and instructions]

**Example:**
```bash
# Example command or usage
command --with arguments
```

### [Workflow Name 2]

[Description of another workflow]

**Steps:**

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Using Bundled Resources

### Scripts

This skill includes helper scripts in the `scripts/` directory:

- **`script_name.py`** - Description of what this script does
  ```bash
  python scripts/script_name.py [arguments]
  ```

### References

Detailed documentation is available in `references/`:

- **`reference_name.md`** - Description of this reference document
  Load when you need [specific information]

To load a reference:
```markdown
Read references/reference_name.md
```

For large references, use grep to find specific sections:
```bash
grep -A 10 "Section Name" references/reference_name.md
```

### Assets

Template files and resources in `assets/`:

- **`templates/template-name/`** - Description of this template
  Copy and customize for [use case]

Usage:
```bash
cp -r assets/templates/template-name/ path/to/destination
```

## Examples

### Example 1: [Common Use Case]

**Scenario:** [Describe the situation]

**Solution:**

1. [Step-by-step solution]
2. [With actual commands]
3. [And expected outputs]

```bash
# Actual command example
command --option value
```

**Expected Result:**
```
Output example
```

### Example 2: [Another Use Case]

**Scenario:** [Describe another situation]

**Solution:**

[Step-by-step solution with examples]

## Best Practices

- [Best practice 1]
- [Best practice 2]
- [Best practice 3]

## Troubleshooting

### [Common Issue 1]

**Problem:** [Description of the issue]

**Solution:** [How to resolve it]

### [Common Issue 2]

**Problem:** [Description of the issue]

**Solution:** [How to resolve it]

## Additional Resources

- [Link to documentation]
- [Link to related skills]
- [Link to tools or services]
