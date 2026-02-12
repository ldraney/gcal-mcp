"""Event tools -- wraps gcal-sdk EventsResource methods."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Annotated, Any

from pydantic import Field

from ..server import mcp, get_client, _parse_json, _error_response, _slim_response


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO 8601 datetime string into a timezone-aware datetime.

    If the string has no timezone info, UTC is assumed.
    """
    if value is None:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@mcp.tool()
def list_events(
    calendar_id: Annotated[str, Field(description="Calendar ID. Use 'primary' for the user's main calendar.")] = "primary",
    time_min: Annotated[str | None, Field(description="Start of time range (RFC3339, e.g. '2024-01-01T00:00:00Z')")] = None,
    time_max: Annotated[str | None, Field(description="End of time range (RFC3339, e.g. '2024-12-31T23:59:59Z')")] = None,
    max_results: Annotated[int, Field(description="Max events to return")] = 25,
    q: Annotated[str | None, Field(description="Free-text search query")] = None,
    single_events: Annotated[bool, Field(description="Expand recurring events into instances")] = True,
    order_by: Annotated[str | None, Field(description="Sort order: 'startTime' or 'updated'")] = "startTime",
) -> str:
    """List events from a Google Calendar.

    Returns events matching the specified criteria. Use time_min/time_max to
    filter by date range, and q for free-text search.
    """
    try:
        client = get_client()
        events = client.events.list(
            calendar_id,
            time_min=_parse_datetime(time_min),
            time_max=_parse_datetime(time_max),
            max_results=max_results,
            q=q,
            single_events=single_events,
            order_by=order_by,
        )
        data = [e.model_dump(by_alias=True) for e in events]
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_event(
    calendar_id: Annotated[str, Field(description="Calendar ID. Use 'primary' for the user's main calendar.")],
    event_id: Annotated[str, Field(description="The event ID to retrieve")],
) -> str:
    """Get a single event by its ID.

    Returns the full event details for the specified event.
    """
    try:
        client = get_client()
        event = client.events.get(calendar_id, event_id)
        data = event.model_dump(by_alias=True)
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def create_event(
    summary: Annotated[str, Field(description="Event title/summary")],
    start: Annotated[str, Field(description="Start time (ISO 8601, e.g. '2024-06-15T10:00:00-06:00')")],
    end: Annotated[str, Field(description="End time (ISO 8601, e.g. '2024-06-15T11:00:00-06:00')")],
    calendar_id: Annotated[str, Field(description="Calendar ID. Use 'primary' for the user's main calendar.")] = "primary",
    description: Annotated[str | None, Field(description="Event description")] = None,
    location: Annotated[str | None, Field(description="Event location")] = None,
    attendees: Annotated[str | list | None, Field(description="Attendees as JSON array of email strings or attendee objects")] = None,
    time_zone: Annotated[str | None, Field(description="Time zone (e.g. 'America/Denver')")] = None,
) -> str:
    """Create a new event on a Google Calendar.

    Creates an event with the specified details. Start and end times must be
    provided as ISO 8601 datetime strings with timezone information.
    """
    try:
        client = get_client()
        parsed_attendees = _parse_json(attendees, "attendees") if attendees is not None else None
        event = client.events.create(
            calendar_id,
            summary=summary,
            description=description,
            location=location,
            start=_parse_datetime(start),
            end=_parse_datetime(end),
            attendees=parsed_attendees,
            time_zone=time_zone,
        )
        data = event.model_dump(by_alias=True)
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def update_event(
    calendar_id: Annotated[str, Field(description="Calendar ID. Use 'primary' for the user's main calendar.")],
    event_id: Annotated[str, Field(description="The event ID to update")],
    body: Annotated[str | dict, Field(description="Complete event body as JSON string or object (full PUT replacement)")],
) -> str:
    """Full update (PUT) of an event -- replaces the entire event resource.

    The body must contain the complete event data. Use patch_event for partial updates.
    """
    try:
        client = get_client()
        parsed_body = _parse_json(body, "body")
        event = client.events.update(calendar_id, event_id, body=parsed_body)
        data = event.model_dump(by_alias=True)
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def patch_event(
    calendar_id: Annotated[str, Field(description="Calendar ID. Use 'primary' for the user's main calendar.")],
    event_id: Annotated[str, Field(description="The event ID to patch")],
    summary: Annotated[str | None, Field(description="New event title/summary")] = None,
    start: Annotated[str | None, Field(description="New start time (ISO 8601)")] = None,
    end: Annotated[str | None, Field(description="New end time (ISO 8601)")] = None,
    description: Annotated[str | None, Field(description="New event description")] = None,
    location: Annotated[str | None, Field(description="New event location")] = None,
    attendees: Annotated[str | list | None, Field(description="New attendees as JSON array of email strings or attendee objects")] = None,
    time_zone: Annotated[str | None, Field(description="Time zone (e.g. 'America/Denver')")] = None,
) -> str:
    """Partial update (PATCH) of an event -- only updates specified fields.

    Only the provided fields will be changed; all other fields remain unchanged.
    """
    try:
        client = get_client()
        parsed_attendees = _parse_json(attendees, "attendees") if attendees is not None else None
        event = client.events.patch(
            calendar_id,
            event_id,
            summary=summary,
            description=description,
            location=location,
            start=_parse_datetime(start),
            end=_parse_datetime(end),
            attendees=parsed_attendees,
            time_zone=time_zone,
        )
        data = event.model_dump(by_alias=True)
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def delete_event(
    calendar_id: Annotated[str, Field(description="Calendar ID. Use 'primary' for the user's main calendar.")],
    event_id: Annotated[str, Field(description="The event ID to delete")],
    send_updates: Annotated[str | None, Field(description="Notification policy: 'all', 'externalOnly', or 'none'")] = None,
) -> str:
    """Delete an event from a Google Calendar.

    Permanently removes the event. Use send_updates to control whether attendees
    are notified about the cancellation.
    """
    try:
        client = get_client()
        client.events.delete(calendar_id, event_id, send_updates=send_updates)
        return json.dumps({"success": True, "deleted": event_id}, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def move_event(
    calendar_id: Annotated[str, Field(description="Source calendar ID")],
    event_id: Annotated[str, Field(description="The event ID to move")],
    destination_calendar_id: Annotated[str, Field(description="Destination calendar ID")],
) -> str:
    """Move an event from one calendar to another.

    Transfers the event to the destination calendar while preserving its data.
    """
    try:
        client = get_client()
        event = client.events.move(calendar_id, event_id, destination_calendar_id)
        data = event.model_dump(by_alias=True)
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def list_event_instances(
    calendar_id: Annotated[str, Field(description="Calendar ID. Use 'primary' for the user's main calendar.")],
    event_id: Annotated[str, Field(description="The recurring event ID")],
    time_min: Annotated[str | None, Field(description="Start of time range (RFC3339)")] = None,
    time_max: Annotated[str | None, Field(description="End of time range (RFC3339)")] = None,
    max_results: Annotated[int, Field(description="Max instances to return")] = 25,
) -> str:
    """List instances of a recurring event.

    Returns individual occurrences of a recurring event within the specified time range.
    """
    try:
        client = get_client()
        events = client.events.instances(
            calendar_id,
            event_id,
            time_min=_parse_datetime(time_min),
            time_max=_parse_datetime(time_max),
            max_results=max_results,
        )
        data = [e.model_dump(by_alias=True) for e in events]
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)
