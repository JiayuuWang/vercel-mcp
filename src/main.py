"""Vercel MCP Server - Type 3 DAuth implementation."""

from dedalus_mcp import MCPServer

from .vercel.tools import (
    list_projects,
    get_project,
    list_deployments,
    get_deployment,
    create_deployment,
    cancel_deployment,
    get_deployment_logs,
    list_domains,
    list_env_vars,
    update_env_var,
)

server = MCPServer("vercel-mcp")

server.collect(
    list_projects,
    get_project,
    list_deployments,
    get_deployment,
    create_deployment,
    cancel_deployment,
    get_deployment_logs,
    list_domains,
    list_env_vars,
    update_env_var,
)


if __name__ == "__main__":
    import asyncio
    asyncio.run(server.serve())