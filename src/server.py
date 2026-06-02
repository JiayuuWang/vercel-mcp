import os
from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings
from vercel import vercel, vercel_tools


def _disable_auto_output_schemas(server: MCPServer) -> None:
    server.tools._build_output_schema = lambda _fn: None


def create_server() -> MCPServer:
    return MCPServer(
        name="vercel-mcp",
        connections=[vercel],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai"),
    )


async def main() -> None:
    server = create_server()
    _disable_auto_output_schemas(server)
    server.collect(*vercel_tools)
    await server.serve(port=8080)