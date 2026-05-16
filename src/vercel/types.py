"""Vercel API types."""

from pydantic import BaseModel, Field
from typing import Optional


class GitSource(BaseModel):
    type: str
    repo_id: str | int
    ref: Optional[str] = None
    sha: Optional[str] = None


class ProjectSummary(BaseModel):
    id: str
    name: str
    framework: Optional[str] = None
    latest_deployment_url: Optional[str] = None


class ProjectsResponse(BaseModel):
    projects: list[ProjectSummary]


class ProjectDetail(BaseModel):
    id: str
    name: str
    framework: Optional[str] = None
    region: Optional[str] = None
    role: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    target: Optional[str] = None
    last_deployments: Optional[list[dict]] = None
    latest_deployments: Optional[list[dict]] = None


class DeploymentSummary(BaseModel):
    uid: str
    name: Optional[str] = None
    url: Optional[str] = None
    state: Optional[str] = None
    created_at: Optional[int] = None
    ready: Optional[int] = None
    created_on: Optional[str] = None


class DeploymentsResponse(BaseModel):
    deployments: list[dict]


class DeploymentDetail(BaseModel):
    uid: str
    name: Optional[str] = None
    url: Optional[str] = None
    state: Optional[str] = None
    ready: Optional[int] = None
    created_at: Optional[int] = None
    created_on: Optional[str] = None
    ready_on: Optional[str] = None


class DeploymentCreated(BaseModel):
    id: str
    url: Optional[str] = None
    name: Optional[str] = None
    state: Optional[str] = None


class DeploymentCanceled(BaseModel):
    uid: str
    state: str


class DeploymentLogs(BaseModel):
    events: list[dict]


class DomainSummary(BaseModel):
    name: str
    apex_name: Optional[str] = None
    verification: Optional[list[dict]] = None


class DomainsResponse(BaseModel):
    domains: list[dict]


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
    value: str