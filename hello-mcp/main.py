from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP(
    name="Hello MCP Server",
    host="0.0.0.0",
    port=3000,
    stateless_http=True,
    debug=False,
)


@mcp.tool(title="Welcome a User", description="Return a friendly welcome message for the user.")
def welcome(name: str = Field(description="The name of the user")) -> str:
    return f"Wecome {name} from this amazing application!"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
