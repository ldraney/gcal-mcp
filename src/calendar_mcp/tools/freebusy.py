"""FreeBusy tools -- wraps gcal-sdk FreeBusyResource methods."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _parse_json, _error_response, _slim_response


def _parse_datetime(value: str) -> datetime:
    """Parse an ISO 8601 datetime string into a timezone-aware datetime.

    If the string has no timezone info, UTC is assumed.
    """
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@mcp.tool()
def query_freebusy(
    calendar_ids: Annotated[str | list, Field(description="Calendar IDs as JSON array of strings, e.g. '[\"primary\", \"other@example.com\"]'")],
    time_min: Annotated[str, Field(description="Start of time range (RFC3339, e.g. '2024-01-01T00:00:00Z')")],
    time_max: Annotated[str, Field(description="End of time range (RFC3339, e.g. '2024-01-31T23:59:59Z')")],
    time_zone: Annotated[str | None, Field(description="Time zone (e.g. 'America/Denver')")] = None,
) -> str:
    """Query free/busy information for one or more calendars.

    Returns busy periods for the specified calendars within the given time range.
    Useful for finding available meeting times.
    """
    try:
        client = get_client()
        parsed_ids = _parse_json(calendar_ids, "calendar_ids")
        response = client.freebusy.query(
            calendar_ids=parsed_ids,
            time_min=_parse_datetime(time_min),
            time_max=_parse_datetime(time_max),
            time_zone=time_zone,
        )
        data = response.model_dump(by_alias=True)
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)
