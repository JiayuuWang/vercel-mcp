# Vercel MCP Server

A Type 3 DAuth MCP server for Vercel API, enabling AI assistants to interact with Vercel projects, deployments, domains, and environment variables.

## Features

- **Projects**: List and get projects
- **Deployments**: List, get, create, cancel deployments, and view deployment logs
- **Domains**: List domains for a project
- **Environment Variables**: List and update environment variables

## Setup

### 1. Obtain Vercel API Token

1. Go to [vercel.com/account/tokens](https://vercel.com/account/tokens)
2. Create a new token with appropriate scopes
3. Copy the token value

### 2. Environment Variables

Configure these environment variables:

```bash
VERCEL_TOKEN=your_vercel_token_here
VERCEL_TEAM_ID=optional_team_id_here  # Only if using a team account
```

## Tools

### Projects

- **list_projects**: List all projects
- **get_project**: Get a specific project by ID or name

### Deployments

- **list_deployments**: List deployments with optional filtering
- **get_deployment**: Get deployment details by ID or URL
- **create_deployment**: Create a new deployment
- **cancel_deployment**: Cancel a building deployment
- **get_deployment_logs**: Get build logs for a deployment

### Domains

- **list_domains**: List all domains for a project

### Environment Variables

- **list_env_vars**: List all environment variables for a project
- **update_env_var**: Update an environment variable

## Usage

```python
from dedalus_mcp import runner

result = await runner.run(
    input="List my Vercel projects",
    mcp_servers=["dedalus-labs/vercel-mcp"],
)
```

## API Reference

This server uses the [Vercel REST API](https://vercel.com/docs/rest-api).

## License

MIT