# command-name

Brief description of what this command does.

## Prompt

Replace this with your command's prompt. This is what gets executed when the command runs.

### Arguments

If your command uses arguments, explain them here:
- `{{args}}` - Contains the arguments passed to the command

### Expected Usage

```
/command-name [arguments]
```

Examples:
- `/command-name value`
- `/command-name --option value`
- `/command-name` (no arguments)

### Command Logic

Write your command's execution logic here. This should be clear step-by-step instructions.

**Steps:**

1. **Parse Arguments** (if applicable)
   - Extract parameters from {{args}}
   - Validate required parameters
   - Set defaults for optional parameters

2. **Execute Main Logic**
   - Describe what the command does
   - Include any tool calls (MCP, skills, etc.)
   - Handle different scenarios

3. **Provide Feedback**
   - Display results clearly
   - Show progress for long operations
   - Report errors helpfully

### Integration

If this command integrates with skills or MCP servers:

**Using Skills:**
```markdown
Use the [skill-name] skill for [purpose]
Reference [skill resource] for [information]
```

**Using MCP Tools:**
```markdown
Use the [tool-name] tool from [mcp-server] with:
- parameter1: value1
- parameter2: value2
```

### Error Handling

Handle errors gracefully:

**If [condition]:**
- Display: "[Clear error message]"
- Suggest: "[How to fix or correct usage]"
- Do not proceed

**If [another condition]:**
- Display: "[Another error message]"
- Provide: "[Alternative approach]"

### Examples

**Example 1: Basic Usage**
```
/command-name basic-argument
```

Expected output:
```
[What the user should see]
```

**Example 2: With Options**
```
/command-name --option value
```

Expected output:
```
[What the user should see]
```

### Notes

- Additional notes or warnings
- Performance considerations
- Best practices for using this command
