"""FreeBusy tools -- wraps gcal-sdk FreeBusyResource methods."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _parse_json, _error_response, _slim_response, _parse_datetime


@mcp.tool()
def query_freebusy(
    calendar_ids: Annotated[str | list, Field(description="Calendar IDs as JSON array of strings, e.g. '[\"primary\", \"other@example.com\"]'")],
    time_min: Annotated[str, Field(description="Start of time range (RFC3339, e.g. '2024-01-01T00:00:00Z')")],
    time_max: Annotated[str, Field(description="End of time range (RFC3339, e.g. '2024-01-31T23:59:59Z')")],
    time_zone: Annotated[str | None, Field(description="Time zone (e.g. 'America/Denver')")] = None,
    group_expansion_max: Annotated[int | None, Field(description="Max number of calendars to expand for group members")] = None,
    calendar_expansion_max: Annotated[int | None, Field(description="Max number of calendars to expand for calendar resources")] = None,
) -> str:
    """Query free/busy information for one or more calendars.

    Returns busy periods for the specified calendars within the given time range.
    Useful for finding available meeting times.
    """
    try:
        client = get_client()
        parsed_ids = _parse_json(calendar_ids, "calendar_ids")
        kwargs: dict = dict(
            calendar_ids=parsed_ids,
            time_min=_parse_datetime(time_min, required=True),
            time_max=_parse_datetime(time_max, required=True),
            time_zone=time_zone,
        )
        if group_expansion_max is not None:
            kwargs["group_expansion_max"] = group_expansion_max
        if calendar_expansion_max is not None:
            kwargs["calendar_expansion_max"] = calendar_expansion_max
        response = client.freebusy.query(**kwargs)
        data = response.model_dump(by_alias=True)
        return json.dumps(_slim_response(data), indent=2, default=str)
    except Exception as exc:
        return _error_response(exc)
