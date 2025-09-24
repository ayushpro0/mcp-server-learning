import asyncio, json
from openai import OpenAI
from mcp.client.stdio import StdioServer
from mcp.client.session import ClientSession
from mcp.client import Client

# Load MCP server config
with open("servers.json") as f:
    server_config = json.load(f)["servers"]

# LLM setup
llm = OpenAI(api_key="YOUR_API_KEY")

async def main():
    # Prepare clients for servers
    clients = {}
    sessions = {}

    for srv in server_config:
        if srv["type"] == "websocket":
            clients[srv["name"]] = await Client.connect(srv["endpoint"])
        elif srv["type"] == "stdio":
            server = StdioServer(srv["command"], srv["args"])
            session = ClientSession(server)
            await session.start()
            sessions[srv["name"]] = session

    query = input("Ask me something: ")

    # Ask LLM which server to use
    decision_prompt = f"""
    You have access to these MCP servers (in JSON):
    {json.dumps(server_config, indent=2)}

    User query: "{query}"
    Decide which server to call and return only the server "name" from the JSON.
    """

    decision = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": decision_prompt}]
    ).choices[0].message.content.strip()

    if decision == "math-server":
        # Extract numbers
        extract_prompt = f"Extract two integers from this query: {query}. Respond only in JSON as {{'a': int, 'b': int}}"
        nums = llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": extract_prompt}]
        ).choices[0].message.content

        numbers = json.loads(nums.replace("'", '"'))
        response = await clients["math-server"].call_tool("add_numbers", numbers)
        print(f"➕ Result: {numbers['a']} + {numbers['b']} = {response}")

    elif decision == "filesystem-server":
        result = await sessions["filesystem-server"].call_tool("list_files", {"path": "."})
        print("📂 Files:", result)

    else:
        print(f"❌ Unknown decision: {decision}")

if __name__ == "__main__":
    asyncio.run(main())
