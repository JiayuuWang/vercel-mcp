"""Vercel MCP tools - Type 3 DAuth implementation."""

from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.auth import Connection, SecretKeys
from pydantic import BaseModel
from typing import Optional, Any


vercel = Connection(
    name="JiayuWang(王嘉宇)-vercel-mcp",
    secrets=SecretKeys(token="VERCEL_TOKEN"),
    base_url="https://api.vercel.com",
    auth_header_format="Bearer {api_key}",
)


class ProjectSummary(BaseModel):
    id: str
    name: str
    framework: Optional[str] = None
    latest_deployment_url: Optional[str] = None


class ProjectsResponse(BaseModel):
    projects: list[ProjectSummary]


class Deployment(BaseModel):
    uid: str
    name: str
    url: Optional[str] = None
    state: Optional[str] = None
    created: Optional[int] = None


class DeploymentsResponse(BaseModel):
    deployments: list[Deployment]


class DeploymentDetail(BaseModel):
    uid: str
    name: str
    url: Optional[str] = None
    state: Optional[str] = None
    created: Optional[int] = None
    ready: Optional[int] = None


class DeploymentCreated(BaseModel):
    id: str
    url: str
    name: str


class DeploymentCanceled(BaseModel):
    uid: str
    state: str


class DeploymentLogs(BaseModel):
    events: list[dict[str, Any]]


class Domain(BaseModel):
    name: str
    verified: bool
    uid: Optional[str] = None


class DomainsResponse(BaseModel):
    domains: list[Domain]


class EnvVarSummary(BaseModel):
    id: str
    key: str
    type: Optional[str] = None
    value: Optional[str] = None
    target: Optional[list[str]] = None


class EnvVarsResponse(BaseModel):
    envs: list[EnvVarSummary]


class EnvVarUpdated(BaseModel):
    id: str
    key: str


async def _get_team_id() -> Optional[str]:
    import os
    return os.getenv("VERCEL_TEAM_ID")


@tool(description="List all projects from Vercel")
async def list_projects(
    limit: Optional[int] = None,
    since: Optional[int] = None,
    until: Optional[int] = None,
) -> ProjectsResponse:
    team_id = await _get_team_id()
    params = {}
    if team_id:
        params["teamId"] = team_id
    if limit is not None:
        params["limit"] = str(limit)
    if since is not None:
        params["since"] = str(since)
    if until is not None:
        params["until"] = str(until)

    ctx = get_context()
    resp = await ctx.dispatch(
        vercel,
        HttpRequest(method=HttpMethod.GET, path="/v10/projects", params=params),
    )

    if resp.success:
        data = resp.response.body if resp.response.body else {}
        return ProjectsResponse(
            projects=[
                ProjectSummary(
                    id=p["id"],
                    name=p["name"],
                    framework=p.get("framework"),
                    latest_deployment_url=(p.get("latestDeployments") or [{}])[0].get("url") if p.get("latestDeployments") else None,
                )
                for p in data.get("projects", [])
            ]
        )
    return ProjectsResponse(projects=[])


@tool(description="Get a specific project by ID or name")
async def get_project(id_or_name: str) -> dict[str, Any]:
    team_id = await _get_team_id()
    params = {}
    if team_id:
        params["teamId"] = team_id

    ctx = get_context()
    resp = await ctx.dispatch(
        vercel,
        HttpRequest(method=HttpMethod.GET, path=f"/v10/projects/{id_or_name}", params=params),
    )

    if resp.success:
        return resp.response.body if resp.response.body else {}
    return {"error": resp.error.message if resp.error else "Request failed"}


@tool(description="List deployments with optional filtering")
async def list_deployments(
    project_id: Optional[str] = None,
    app: Optional[str] = None,
    limit: Optional[int] = None,
    since: Optional[int] = None,
    until: Optional[int] = None,
    state: Optional[str] = None,
    target: Optional[str] = None,
) -> DeploymentsResponse:
    team_id = await _get_team_id()
    params = {}
    if team_id:
        params["teamId"] = team_id
    if project_id:
        params["projectId"] = project_id
    if app:
        params["app"] = app
    if limit is not None:
        params["limit"] = str(limit)
    if since is not None:
        params["since"] = str(since)
    if until is not None:
        params["until"] = str(until)
    if state:
        params["state"] = state
    if target:
        params["target"] = target

    ctx = get_context()
    resp = await ctx.dispatch(
        vercel,
        HttpRequest(method=HttpMethod.GET, path="/v6/deployments", params=params),
    )

    if resp.success:
        data = resp.response.body if resp.response.body else {}
        return DeploymentsResponse(deployments=data.get("deployments", []))
    return DeploymentsResponse(deployments=[])


@tool(description="Get deployment details by ID or URL")
async def get_deployment(
    id_or_url: str,
    with_git_repo_info: Optional[bool] = None,
) -> dict[str, Any]:
    team_id = await _get_team_id()
    params = {}
    if team_id:
        params["teamId"] = team_id
    if with_git_repo_info:
        params["withGitRepoInfo"] = "true"

    ctx = get_context()
    resp = await ctx.dispatch(
        vercel,
        HttpRequest(method=HttpMethod.GET, path=f"/v13/deployments/{id_or_url}", params=params),
    )

    if resp.success:
        return resp.response.body if resp.response.body else {}
    return {"error": resp.error.message if resp.error else "Request failed"}


@tool(description="Create a new deployment")
async def create_deployment(
    name: str,
    project: Optional[str] = None,
    target: Optional[str] = None,
    git_source: Optional[dict[str, Any]] = None,
    force_new: bool = False,
) -> dict[str, Any]:
    team_id = await _get_team_id()
    params = {}
    if team_id:
        params["teamId"] = team_id
    if force_new:
        params["forceNew"] = "1"

    payload: dict[str, Any] = {"name": name}
    if project:
        payload["project"] = project
    if target:
        payload["target"] = target
    if git_source:
        payload["gitSource"] = git_source

    ctx = get_context()
    resp = await ctx.dispatch(
        vercel,
        HttpRequest(method=HttpMethod.POST, path="/v13/deployments", params=params, body=payload),
    )

    if resp.success:
        return resp.response.body if resp.response.body else {}
    return {"error": resp.error.message if resp.error else "Request failed"}


@tool(description="Cancel a deployment that is currently building")
async def cancel_deployment(id: str) -> dict[str, Any]:
    team_id = await _get_team_id()
    params = {}
    if team_id:
        params["teamId"] = team_id

    ctx = get_context()
    resp = await ctx.dispatch(
        vercel,
        HttpRequest(method=HttpMethod.PATCH, path=f"/v12/deployments/{id}/cancel", params=params),
    )

    if resp.success:
        return resp.response.body if resp.response.body else {}
    return {"error": resp.error.message if resp.error else "Request failed"}


@tool(description="Get build logs for a deployment")
async def get_deployment_logs(
    id_or_url: str,
    direction: Optional[str] = None,
    follow: Optional[int] = None,
    limit: Optional[int] = None,
    since: Optional[int] = None,
    until: Optional[int] = None,
) -> dict[str, Any]:
    team_id = await _get_team_id()
    params = {}
    if team_id:
        params["teamId"] = team_id
    if direction:
        params["direction"] = direction
    if follow is not None:
        params["follow"] = str(follow)
    if limit is not None:
        params["limit"] = str(limit)
    if since is not None:
        params["since"] = str(since)
    if until is not None:
        params["until"] = str(until)

    ctx = get_context()
    resp = await ctx.dispatch(
        vercel,
        HttpRequest(method=HttpMethod.GET, path=f"/v3/deployments/{id_or_url}/events", params=params),
    )

    if resp.success:
        return resp.response.body if resp.response.body else {}
    return {"error": resp.error.message if resp.error else "Request failed"}


@tool(description="List all domains for a project")
async def list_domains(id_or_name: str) -> dict[str, Any]:
    team_id = await _get_team_id()
    params = {}
    if team_id:
        params["teamId"] = team_id

    ctx = get_context()
    resp = await ctx.dispatch(
        vercel,
        HttpRequest(method=HttpMethod.GET, path=f"/v9/projects/{id_or_name}/domains", params=params),
    )

    if resp.success:
        return resp.response.body if resp.response.body else {}
    return {"error": resp.error.message if resp.error else "Request failed"}


@tool(description="List all environment variables for a project")
async def list_env_vars(id_or_name: str) -> dict[str, Any]:
    team_id = await _get_team_id()
    params = {}
    if team_id:
        params["teamId"] = team_id

    ctx = get_context()
    resp = await ctx.dispatch(
        vercel,
        HttpRequest(method=HttpMethod.GET, path=f"/v9/projects/{id_or_name}/env", params=params),
    )

    if resp.success:
        return resp.response.body if resp.response.body else {}
    return {"error": resp.error.message if resp.error else "Request failed"}


@tool(description="Update an environment variable")
async def update_env_var(
    id_or_name: str,
    env_id: str,
    value: str,
    type: Optional[str] = None,
    target: Optional[list[str]] = None,
) -> dict[str, Any]:
    team_id = await _get_team_id()
    params = {}
    if team_id:
        params["teamId"] = team_id

    payload: dict[str, Any] = {"value": value}
    if type:
        payload["type"] = type
    if target:
        payload["target"] = target

    ctx = get_context()
    resp = await ctx.dispatch(
        vercel,
        HttpRequest(
            method=HttpMethod.PATCH,
            path=f"/v9/projects/{id_or_name}/env/{env_id}",
            params=params,
            body=payload,
        ),
    )

    if resp.success:
        return resp.response.body if resp.response.body else {}
    return {"error": resp.error.message if resp.error else "Request failed"}


vercel_tools = [
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
]

__all__ = ["vercel_tools", "vercel"]