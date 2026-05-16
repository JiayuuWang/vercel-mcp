"""Vercel API configuration."""

BASE_URL = "https://api.vercel.com"


def get_token() -> str:
    import os
    return os.environ.get("VERCEL_TOKEN", "")


def get_team_id() -> str | None:
    import os
    return os.environ.get("VERCEL_TEAM_ID")