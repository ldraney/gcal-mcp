"""Calendar tools -- wraps gcal-sdk CalendarsResource methods."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _error_response, _slim_response


@mcp.tool()
def list_calendars(
    show_deleted: Annotated[bool, Field(description="Whether to show deleted calendars")] = False,
    show_hidden: Annotated[bool, Field(description="Whether to show hidden calendars")] = False,
    max_results: Annotated[int, Field(description="Max calendars to return")] = 100,
) -> str:
    """List all calendars in the user's calendar list.

    Returns basic info about each calendar the user has access to.
    """
    try:
        client = get_client()
        calendars = client.calendars.list(
            show_deleted=show_deleted,
            show_hidden=show_hidden,
            max_results=max_results,
        )
        data = [c.model_dump(by_alias=True) for c in calendars]
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_calendar(
    calendar_id: Annotated[str, Field(description="Calendar ID. Use 'primary' for the user's main calendar.")] = "primary",
) -> str:
    """Get details about a specific calendar.

    Returns the user's view of the calendar including color, notification
    settings, and access role.
    """
    try:
        client = get_client()
        calendar = client.calendars.get(calendar_id)
        data = calendar.model_dump(by_alias=True)
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def create_calendar(
    summary: Annotated[str, Field(description="Title of the new calendar")],
    description: Annotated[str | None, Field(description="Description of the calendar")] = None,
    time_zone: Annotated[str | None, Field(description="Time zone (e.g. 'America/Denver')")] = None,
    location: Annotated[str | None, Field(description="Geographic location")] = None,
) -> str:
    """Create a new secondary calendar.

    Creates a new calendar owned by the user. The primary calendar cannot
    be created this way.
    """
    try:
        client = get_client()
        calendar = client.calendars.create(
            summary,
            description=description,
            time_zone=time_zone,
            location=location,
        )
        data = calendar.model_dump(by_alias=True)
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def delete_calendar(
    calendar_id: Annotated[str, Field(description="Calendar ID to delete. Cannot be 'primary'.")],
) -> str:
    """Delete a secondary calendar.

    Permanently deletes the calendar and all its events. The primary calendar
    cannot be deleted.
    """
    try:
        client = get_client()
        client.calendars.delete(calendar_id)
        return json.dumps({"success": True, "deleted": calendar_id}, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def clear_calendar(
    calendar_id: Annotated[str, Field(description="Calendar ID to clear. Use 'primary' for the user's main calendar.")] = "primary",
) -> str:
    """Clear all events from a calendar.

    Removes all events from the specified calendar. The calendar itself is
    not deleted. WARNING: This is destructive and irreversible.
    """
    try:
        client = get_client()
        client.calendars.clear(calendar_id)
        return json.dumps({"success": True, "cleared": calendar_id}, indent=2)
    except Exception as exc:
        return _error_response(exc)
