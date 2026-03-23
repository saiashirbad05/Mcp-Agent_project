import asyncio
import json
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from weather_service import fetch_weather_by_city

server = Server("weather-mcp-server")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_weather",
            description="Get current weather for a city using the Open-Meteo API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name such as Delhi, London, or Tokyo.",
                    }
                },
                "required": ["city"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> types.CallToolResult:
    if name != "get_weather":
        raise ValueError(f"Unknown tool: {name}")

    city = str((arguments or {}).get("city", "")).strip()
    if not city:
        raise ValueError("The 'city' argument is required.")

    weather_data = await fetch_weather_by_city(city)

    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=json.dumps(weather_data, ensure_ascii=True),
            )
        ],
        structuredContent=weather_data,
    )


async def main() -> None:
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
