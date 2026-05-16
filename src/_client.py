"""Test client for Vercel MCP server using SecretValues."""

from dedalus_mcp.client import MCPClient, SecretValue
import asyncio


async def main():
    token = SecretValue.from_env("VERCEL_TOKEN")
    client = await MCPClient.connect("http://localhost:8000/mcp")

    tools = await client.list_tools()
    print("Available tools:", [t.name for t in tools])

    result = await client.call_tool("list_projects", {})
    print(result)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())