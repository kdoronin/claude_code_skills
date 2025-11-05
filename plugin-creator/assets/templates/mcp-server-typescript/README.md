# MCP Server Template (TypeScript)

TypeScript template for creating MCP servers for Claude Code.

## Quick Start

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Customize the server**
   - Edit `src/index.ts` to add your tools and resources
   - Update `package.json` with your project details

3. **Build**
   ```bash
   npm run build
   ```

4. **Test locally**
   ```bash
   npm start
   ```

5. **Add to Claude Code**
   Add to `~/.claude/config.json`:
   ```json
   {
     "mcpServers": {
       "your-server-name": {
         "command": "node",
         "args": ["/path/to/dist/index.js"]
       }
     }
   }
   ```

## Project Structure

```
mcp-server-template/
├── src/
│   └── index.ts           # Main server implementation
├── dist/                  # Compiled output (generated)
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
└── README.md             # This file
```

## Adding Tools

Add new tools in `src/index.ts`:

```typescript
// In ListToolsRequestSchema handler
{
  name: "my_new_tool",
  description: "Description of what this tool does",
  inputSchema: {
    type: "object",
    properties: {
      param1: { type: "string", description: "Parameter description" }
    },
    required: ["param1"]
  }
}

// In CallToolRequestSchema handler
case "my_new_tool":
  return await this.handleMyNewTool(args);

// Add handler method
private async handleMyNewTool(args: any) {
  // Implementation
  return {
    content: [
      { type: "text", text: JSON.stringify(result) }
    ]
  };
}
```

## Adding Resources

Add new resources in `src/index.ts`:

```typescript
// In ListResourcesRequestSchema handler
{
  uri: "resource://my-server/my-resource",
  name: "My Resource",
  description: "Description of this resource",
  mimeType: "application/json"
}

// In ReadResourceRequestSchema handler
case "resource://my-server/my-resource":
  return {
    contents: [{
      uri,
      mimeType: "application/json",
      text: JSON.stringify(data)
    }]
  };
```

## Configuration

Set environment variables:
```bash
export DEBUG=true
# Add your custom environment variables
```

## Development

```bash
# Watch mode
npm run dev

# Run tests
npm test

# Lint code
npm run lint
```

## Deployment

1. Build the project: `npm run build`
2. Publish to npm or distribute the `dist` folder
3. Users can install globally: `npm install -g your-server-name`

## Best Practices

- Validate all tool inputs
- Provide clear error messages
- Use TypeScript types for safety
- Handle async operations properly
- Clean up resources on shutdown
- Add comprehensive tests

## Resources

- [MCP Specification](https://modelcontextprotocol.io)
- [TypeScript MCP SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Claude Code Documentation](https://docs.claude.com/claude-code)
