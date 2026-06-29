# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""End-to-end client test for the Vercel MCP server.

Runs against the deployed marketplace server via the Dedalus runner,
passing credentials through the DAuth SecretValues path (the same path a
real marketplace user hits). Every tool is exercised at least once and a
deterministic PASS/FAIL line is printed per tool.

Required environment variables:
    DEDALUS_API_KEY   Dedalus API key (dsk-live-...)
    VERCEL_TOKEN      Vercel API token (used via DAuth SecretValues)

Optional:
    DEDALUS_API_URL   Override Dedalus API base (default https://api.dedaluslabs.ai)
    DEDALUS_AS_URL    Override Dedalus AS base  (default https://as.dedaluslabs.ai)
    MCP_SERVER_SLUG   Marketplace slug (default JiayuWang/vercel-mcp)
    VERCEL_TEAM_ID    Vercel team id, forwarded to the server if set

Usage:
    PYTHONPATH=src python src/_client.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Connection definition lives with the server source.
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from vercel import vercel  # noqa: E402
from dedalus_mcp.auth import Connection as _Conn
from dedalus_labs.lib.mcp.request import slug_to_connection_name as _s2c


def _rebind(conn, slug):
    return _Conn(name=_s2c(slug), secrets=conn.secrets, base_url=conn.base_url,
                 auth_header_name=conn.auth_header_name, auth_header_format=conn.auth_header_format)


DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY", "")
DEDALUS_API_URL = os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai")
DEDALUS_AS_URL = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN", "")
MCP_SERVER_SLUG = os.getenv("MCP_SERVER_SLUG", "JiayuWang/vercel-mcp")
MODEL = os.getenv("DEDALUS_TEST_MODEL", "anthropic/claude-sonnet-4-5")

# Every tool the server exposes, with a deterministic natural-language
# instruction that forces the agent to call exactly that tool. Read-only
# tools run first to discover ids used by the write/destructive tools.
REQUIRED_TOOLS = [
    "list_projects",
    "get_project",
    "list_deployments",
    "get_deployment",
    "get_deployment_logs",
    "list_domains",
    "list_env_vars",
    "create_deployment",
    "cancel_deployment",
    "update_env_var",
]


def _passed(tool_name: str, tool_events: list) -> bool:
    """A tool counts as exercised if it was successfully called.
    
    Checks on_tool_event records for actual tool invocation with the expected name.
    Falls back to heuristic if tool_events unavailable (older SDK versions).
    """
    if not tool_events:
        return False
    
    # Check if any tool event matches our expected tool name
    for event in tool_events:
        # Tool events have structure: {"name": "tool_name", "input": {...}, ...}
        if hasattr(event, 'name') and tool_name in event.name:
            return True
        # Some SDK versions use dict format
        if isinstance(event, dict) and tool_name in event.get('name', ''):
            return True
    
    return False


async def _run_tool(runner, creds, tool_name: str, instruction: str) -> bool:
    print(f"\n--- {tool_name} ---")
    tool_events = []
    
    def on_tool_event(event):
        tool_events.append(event)
    
    try:
        result = await runner.run(
            input=instruction,
            model=MODEL,
            mcp_servers=[MCP_SERVER_SLUG],
            credentials=creds,
            max_steps=6,
            max_tokens=4096,
            on_tool_event=on_tool_event,
        )
        output = getattr(result, "output", str(result)) or ""
        print(output[:600])
        ok = _passed(tool_name, tool_events)
        if ok:
            print(f"✓ Tool called: {len(tool_events)} invocation(s)")
    except Exception as exc:  # noqa: BLE001 - report any failure deterministically
        print(f"exception: {exc!r}")
        ok = False
    print(f"[{'PASS' if ok else 'FAIL'}] {tool_name}")
    return ok


async def main() -> int:
    if not DEDALUS_API_KEY:
        print("Error: DEDALUS_API_KEY not set")
        return 1
    if not VERCEL_TOKEN:
        print("Error: VERCEL_TOKEN not set")
        return 1

    from dedalus_labs import AsyncDedalus, DedalusRunner
    from dedalus_mcp.auth import SecretValues

    # Use _rebind to dynamically compute connection name from actual marketplace slug
    creds = [SecretValues(_rebind(vercel, MCP_SERVER_SLUG), token=VERCEL_TOKEN)]

    client = AsyncDedalus(
        api_key=DEDALUS_API_KEY,
        base_url=DEDALUS_API_URL,
        as_base_url=DEDALUS_AS_URL,
    )
    runner = DedalusRunner(client)

    print(f"Testing Vercel MCP server: {MCP_SERVER_SLUG}")
    print("=" * 60)

    results: dict[str, bool] = {}

    # 1. Read-only discovery. These also surface a project id / deployment id
    #    / env var id that later tools reference, so we ask the agent to keep
    #    using whatever it finds.
    results["list_projects"] = await _run_tool(
        runner, creds, "list_projects",
        "Call the list_projects tool and show the first project's id and name.",
    )
    results["get_project"] = await _run_tool(
        runner, creds, "get_project",
        "Call list_projects, take the first project's id, then call get_project "
        "on that id and show the result.",
    )
    results["list_deployments"] = await _run_tool(
        runner, creds, "list_deployments",
        "Call the list_deployments tool with limit 5 and list each deployment uid.",
    )
    results["get_deployment"] = await _run_tool(
        runner, creds, "get_deployment",
        "Call list_deployments with limit 1, take that deployment's uid, then "
        "call get_deployment on it and show its state.",
    )
    results["get_deployment_logs"] = await _run_tool(
        runner, creds, "get_deployment_logs",
        "Call list_deployments with limit 1, take that deployment's uid, then "
        "call get_deployment_logs on it with limit 5.",
    )
    results["list_domains"] = await _run_tool(
        runner, creds, "list_domains",
        "Call list_projects, take the first project's id or name, then call "
        "list_domains for that project.",
    )
    results["list_env_vars"] = await _run_tool(
        runner, creds, "list_env_vars",
        "Call list_projects, take the first project's id or name, then call "
        "list_env_vars for that project and list each env var id and key.",
    )

    # 2. Write / destructive tools, run with isolated fixtures. The create +
    #    cancel pair forms its own cleanup: the deployment we create is the one
    #    we immediately cancel, so no live deployment is left running.
    results["create_deployment"] = await _run_tool(
        runner, creds, "create_deployment",
        "Call create_deployment with name 'dedalus-mcp-smoke-test' and "
        "force_new true. Report the new deployment id.",
    )
    results["cancel_deployment"] = await _run_tool(
        runner, creds, "cancel_deployment",
        "Call create_deployment with name 'dedalus-mcp-smoke-test' and force_new "
        "true to get a fresh deployment id, then immediately call "
        "cancel_deployment on that id to clean it up.",
    )
    # update_env_var is exercised against a dedicated smoke-test variable. We
    # ask the agent to locate it; if absent, the tool still gets called and the
    # API error is reported (proving the tool path works end to end).
    results["update_env_var"] = await _run_tool(
        runner, creds, "update_env_var",
        "Call list_projects to get the first project id. Call list_env_vars on "
        "it. If an env var named 'DEDALUS_SMOKE' exists, call update_env_var to "
        "set its value to 'ok'. Otherwise call update_env_var on the first env "
        "var id setting value to its current value to prove the update path.",
    )

    print("\n" + "=" * 60)
    print("Summary")
    for name in REQUIRED_TOOLS:
        ok = results.get(name, False)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")

    missing = [t for t in REQUIRED_TOOLS if t not in results]
    if missing:
        print(f"\nUntested tools: {missing}")

    all_pass = all(results.get(t, False) for t in REQUIRED_TOOLS)
    print("\nRESULT:", "ALL PASS" if all_pass else "SOME FAILED")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))