#!/usr/bin/env python3
"""
MCP Server Template using FastMCP

This template provides a starting point for creating MCP servers with Python.
"""

import os
import json
from datetime import datetime
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource


class Config:
    """Server configuration loaded from environment variables"""

    def __init__(self):
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        # Add your configuration variables here

    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            "debug": self.debug,
        }


class MCPServerTemplate:
    """Main MCP Server implementation"""

    def __init__(self):
        self.config = Config()
        self.server = Server("mcp-server-template")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup tool and resource handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="example_tool",
                    description="Example tool that demonstrates basic functionality",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to process",
                            }
                        },
                        "required": ["message"],
                    },
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""
            try:
                if name == "example_tool":
                    return await self._handle_example_tool(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="resource://example/config",
                    name="Example Configuration",
                    description="Example resource demonstrating resource pattern",
                    mimeType="application/json",
                )
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read resource content"""
            if uri == "resource://example/config":
                return json.dumps(self.config.to_dict(), indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")

    async def _handle_example_tool(self, args: dict) -> list[TextContent]:
        """
        Handle example tool execution

        Args:
            args: Tool arguments including 'message'

        Returns:
            List of TextContent with the result
        """
        if "message" not in args:
            raise ValueError("Missing required parameter: message")

        result = {
            "processed": True,
            "message": args["message"],
            "timestamp": datetime.now().isoformat(),
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def run(self):
        """Start the MCP server"""
        if self.config.debug:
            import sys

            print("MCP Server running in debug mode", file=sys.stderr)

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def main():
    """Main entry point"""
    import asyncio

    try:
        server = MCPServerTemplate()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import sys

        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
