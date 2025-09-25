# custom_server.py
from mcp.server.fastmcp import FastMCP, Context

app = FastMCP("math-server")

@app.tool()
def add_numbers(ctx: Context, a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b

if __name__ == "__main__":
    app.run()
