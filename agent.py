import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

MODEL_ID = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MCP_SERVER_PATH = os.path.join(BASE_DIR, "weather_mcp_server.py")

root_agent = LlmAgent(
    name="mcp_agent",
    model=MODEL_ID,
    description="An MCP-powered weather agent.",
    instruction=(
        "You are mcp-agent, a weather assistant. "
        "For every request, you must call the get_weather MCP tool before answering. "
        "After the tool returns data, you must return only valid JSON with exactly these keys: "
        "\"city\", \"weather_data\", \"answer\", \"status\". "
        "Copy the complete MCP tool output into the weather_data field. "
        "Set status to success when the tool call succeeds. "
        "The answer field must be a short natural-language explanation based only on the tool data. "
        "If the tool fails or the city cannot be found, return only valid JSON in this exact form: "
        "{\"city\":\"<requested city>\",\"weather_data\":null,\"answer\":\"<clear error message>\",\"status\":\"error\"}. "
        "Do not wrap JSON in markdown. "
        "Do not add extra keys."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="python3",
                    args=[MCP_SERVER_PATH],
                ),
                timeout=30,
            ),
            tool_filter=["get_weather"],
        )
    ],
)
