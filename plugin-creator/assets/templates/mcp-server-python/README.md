# MCP Server Template (Python/FastMCP)

Python template for creating MCP servers for Claude Code using FastMCP.

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -e .
   # Or for development
   pip install -e ".[dev]"
   ```

2. **Customize the server**
   - Edit `app/main.py` to add your tools and resources
   - Update `pyproject.toml` with your project details

3. **Test locally**
   ```bash
   python -m app.main
   # Or using the installed script
   mcp-server-template
   ```

4. **Add to Claude Code**
   Add to `~/.claude/config.json`:
   ```json
   {
     "mcpServers": {
       "your-server-name": {
         "command": "mcp-server-template"
       }
     }
   }
   ```

## Project Structure

```
mcp-server-template/
├── app/
│   ├── __init__.py
│   └── main.py            # Main server implementation
├── tests/                 # Test files
├── pyproject.toml         # Project configuration and dependencies
└── README.md             # This file
```

## Adding Tools

Add new tools in `app/main.py`:

```python
# In list_tools handler
@self.server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="my_new_tool",
            description="Description of what this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param1"]
            }
        )
    ]

# In call_tool handler
if name == "my_new_tool":
    return await self._handle_my_new_tool(arguments)

# Add handler method
async def _handle_my_new_tool(self, args: dict) -> list[TextContent]:
    """Handle my new tool"""
    # Implementation
    result = {"status": "success"}
    return [TextContent(type="text", text=json.dumps(result))]
```

## Adding Resources

Add new resources in `app/main.py`:

```python
# In list_resources handler
@self.server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="resource://my-server/my-resource",
            name="My Resource",
            description="Description of this resource",
            mimeType="application/json"
        )
    ]

# In read_resource handler
@self.server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "resource://my-server/my-resource":
        return json.dumps(data)
    raise ValueError(f"Unknown resource: {uri}")
```

## Configuration

Set environment variables:
```bash
export DEBUG=true
# Add your custom environment variables
```

## Development

```bash
# Format code
black app/

# Lint code
ruff check app/

# Run tests
pytest

# Run with debug
DEBUG=true python -m app.main
```

## Deployment

### Option 1: pip install
```bash
pip install .
# Server available as 'mcp-server-template' command
```

### Option 2: PyPI
```bash
# Build
python -m build

# Publish
twine upload dist/*
```

### Option 3: Direct execution
```bash
# Users can run directly
python -m app.main
```

## Best Practices

- Use type hints for all functions
- Validate inputs in tool handlers
- Provide clear error messages
- Use async/await for I/O operations
- Add docstrings to all functions
- Write comprehensive tests

## Testing

```python
# tests/test_tools.py
import pytest
from app.main import MCPServerTemplate

@pytest.mark.asyncio
async def test_example_tool():
    server = MCPServerTemplate()
    result = await server._handle_example_tool({"message": "test"})
    assert len(result) > 0
    assert "processed" in result[0].text
```

## Resources

- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Claude Code Documentation](https://docs.claude.com/claude-code)
