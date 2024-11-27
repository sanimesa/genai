# /// script
# dependencies = [
#   "mcp"
# ]
# ///
# Simple MCP Server
import json
from collections.abc import Sequence
from typing import Any
from mcp.server import Server
import mcp.types as types
import asyncio
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Create a server instance
app = Server("heartbeat-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_heartbeat",
            description="Get a heartbeat",
            inputSchema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "string",
                        "description": "user name"
                    },
                },
                "required": ["user"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for heartbeat."""
    print(f"call_tool invoked with parameters: {name}, {arguments}")
    
    if name != "get_heartbeat":
        raise ValueError(f"Unknown tool: {name}")

    if not isinstance(arguments, dict) or "user" not in arguments:
        raise ValueError("Invalid arguments")

    reply = {
        "text": f"Hello {arguments['user']}, my heart beats for you!"
    }

    return [
        TextContent(
            type="text",
            text=json.dumps(reply, indent=2)
        )
    ]


async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
