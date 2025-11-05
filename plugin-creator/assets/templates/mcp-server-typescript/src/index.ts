#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

/**
 * Configuration interface
 */
interface Config {
  // Add your configuration fields here
  debug?: boolean;
}

/**
 * Load configuration from environment variables
 */
function loadConfig(): Config {
  return {
    debug: process.env.DEBUG === 'true',
  };
}

/**
 * MCP Server implementation
 */
class MCPServer {
  private server: Server;
  private config: Config;

  constructor() {
    this.config = loadConfig();
    this.server = new Server(
      {
        name: "mcp-server-template",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
          resources: {},
        },
      }
    );

    this.setupHandlers();
  }

  /**
   * Setup request handlers
   */
  private setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "example_tool",
          description: "Example tool that demonstrates basic functionality",
          inputSchema: {
            type: "object",
            properties: {
              message: {
                type: "string",
                description: "Message to process",
              },
            },
            required: ["message"],
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "example_tool":
            return await this.handleExampleTool(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        return {
          content: [
            {
              type: "text",
              text: `Error: ${errorMessage}`,
            },
          ],
          isError: true,
        };
      }
    });

    // List available resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
      resources: [
        {
          uri: "resource://example/config",
          name: "Example Configuration",
          description: "Example resource demonstrating resource pattern",
          mimeType: "application/json",
        },
      ],
    }));

    // Read resources
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;

      try {
        switch (uri) {
          case "resource://example/config":
            return {
              contents: [
                {
                  uri,
                  mimeType: "application/json",
                  text: JSON.stringify(this.config, null, 2),
                },
              ],
            };
          default:
            throw new Error(`Unknown resource: ${uri}`);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        throw new Error(`Failed to read resource ${uri}: ${errorMessage}`);
      }
    });
  }

  /**
   * Example tool handler
   */
  private async handleExampleTool(args: any) {
    if (!args.message) {
      throw new Error("Missing required parameter: message");
    }

    const result = {
      processed: true,
      message: args.message,
      timestamp: new Date().toISOString(),
    };

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  /**
   * Start the server
   */
  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);

    if (this.config.debug) {
      console.error("MCP Server running in debug mode");
    }
  }
}

/**
 * Main entry point
 */
async function main() {
  try {
    const server = new MCPServer();
    await server.run();
  } catch (error) {
    console.error("Fatal error:", error);
    process.exit(1);
  }
}

main();
