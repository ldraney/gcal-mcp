"""MCP server entry point -- FastMCP app and GCalClient lifecycle."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP
from gcal_sdk import GCalClient

mcp = FastMCP("calendar")

# ---------------------------------------------------------------------------
# Shared client instance
# ---------------------------------------------------------------------------

_client: GCalClient | None = None


def get_client() -> GCalClient:
    """Return the shared GCalClient, creating it on first call.

    The client loads credentials from ~/secrets/google-oauth/ by default.
    """
    global _client
    if _client is None:
        _client = GCalClient()
    return _client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_json(value: str | dict | list | None, name: str) -> Any:
    """Parse a JSON string into a Python object, or pass through if already parsed."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON for parameter '{name}': {exc}") from exc


def _error_response(exc: Exception) -> str:
    """Format an exception into a user-friendly error string."""
    return json.dumps({"error": True, "message": str(exc)}, indent=2)


# ---------------------------------------------------------------------------
# Response slimming -- strip Calendar API noise to reduce token usage
# ---------------------------------------------------------------------------

# Keys that are always API machinery noise
_ALWAYS_STRIP_KEYS = {"etag", "kind"}


def _slim_response(data: Any) -> Any:
    """Recursively strip metadata noise from a Google Calendar API response.

    Removes null values, empty strings, empty lists, redundant keys, and
    other noise that inflates token usage without adding information value.
    """
    if isinstance(data, list):
        return [_slim_response(item) for item in data]

    if not isinstance(data, dict):
        return data

    result: dict[str, Any] = {}

    for key, value in data.items():
        # --- Strip null values ---
        if value is None:
            continue

        # --- Strip empty strings and empty lists ---
        if value == "" or value == []:
            continue

        # --- Strip keys that are always API noise ---
        if key in _ALWAYS_STRIP_KEYS:
            continue

        # --- Strip iCalUID (redundant with id) ---
        if key == "iCalUID":
            continue

        # --- Strip reminders when just default ---
        if key == "reminders" and isinstance(value, dict):
            if value == {"useDefault": True} or value == {"use_default": True}:
                continue

        # --- Strip sequence when 0 ---
        if key == "sequence" and value == 0:
            continue

        # --- Strip colorId when not meaningfully set ---
        if key == "colorId" and value is None:
            continue

        # --- Recurse into nested structures ---
        value = _slim_response(value)

        result[key] = value

    return result


# ---------------------------------------------------------------------------
# Register tool modules -- each module calls @mcp.tool() at import time
# ---------------------------------------------------------------------------

from .tools import register_all_tools  # noqa: E402

register_all_tools()


def main() -> None:
    """Entry point for the console script."""
    mcp.run()
