# app.py
import asyncio
from openai import OpenAI
from mcp.client.stdio import StdioServer
from mcp.client.session import ClientSession
from mcp.client import Client

# LLM setup
llm = OpenAI(api_key="YOUR_API_KEY")

async def main():
    # Connect to custom math server (addition)
    math_client = await Client.connect("ws://localhost:8000")

    # Connect to filesystem MCP server via npx stdio
    fs_server = StdioServer("npx", ["-y", "@modelcontextprotocol/server-filesystem", "--root", "."])
    fs_session = ClientSession(fs_server)
    await fs_session.start()

    query = input("Ask me something: ")

    decision_prompt = f"""
    You have access to two tools:
    1. Math server (for adding numbers).
    2. Filesystem server (for listing files).
    User asked: {query}
    Decide which tool to call and ONLY output: 'math' or 'fs'.
    """

    decision = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": decision_prompt}]
    ).choices[0].message.content.strip().lower()

    if "math" in decision:
        # Ask LLM to extract numbers
        extract_prompt = f"Extract two integers from this query: {query}. Respond only in JSON as {{'a': int, 'b': int}}"
        nums = llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": extract_prompt}]
        ).choices[0].message.content

        import json
        numbers = json.loads(nums.replace("'", '"'))

        response = await math_client.call_tool("add_numbers", numbers)
        print(f"➕ Result: {numbers['a']} + {numbers['b']} = {response}")
    elif "fs" in decision:
        result = await fs_session.call_tool("list_files", {"path": "."})
        print("📂 Files:", result)
    else:
        print("LLM could not decide.")

if __name__ == "__main__":
    asyncio.run(main())
