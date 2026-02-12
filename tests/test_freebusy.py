"""Tests for freebusy tools.

These tests mock the GCalClient so no real API calls are made.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from gcal_sdk.models import FreeBusyResponse, CalendarFreeBusy, BusyPeriod


# ---------------------------------------------------------------------------
# query_freebusy
# ---------------------------------------------------------------------------


class TestQueryFreeBusy:
    def test_query_freebusy_basic(self, mock_client):
        from calendar_mcp.tools.freebusy import query_freebusy

        mock_response = FreeBusyResponse(
            kind="calendar#freeBusy",
            timeMin=datetime(2024, 1, 1, tzinfo=timezone.utc),
            timeMax=datetime(2024, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
            calendars={
                "primary": CalendarFreeBusy(
                    busy=[
                        BusyPeriod(
                            start=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
                            end=datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc),
                        )
                    ]
                )
            },
        )
        mock_client.freebusy.query.return_value = mock_response
        result = query_freebusy(
            calendar_ids='["primary"]',
            time_min="2024-01-01T00:00:00Z",
            time_max="2024-01-31T23:59:59Z",
        )
        parsed = json.loads(result)
        assert "calendars" in parsed
        assert "primary" in parsed["calendars"]
        assert len(parsed["calendars"]["primary"]["busy"]) == 1
        mock_client.freebusy.query.assert_called_once_with(
            calendar_ids=["primary"],
            time_min=datetime(2024, 1, 1, tzinfo=timezone.utc),
            time_max=datetime(2024, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
            time_zone=None,
        )

    def test_query_freebusy_list_input(self, mock_client):
        from calendar_mcp.tools.freebusy import query_freebusy

        mock_response = FreeBusyResponse(
            calendars={
                "primary": CalendarFreeBusy(busy=[]),
                "other@example.com": CalendarFreeBusy(busy=[]),
            }
        )
        mock_client.freebusy.query.return_value = mock_response
        result = query_freebusy(
            calendar_ids=["primary", "other@example.com"],
            time_min="2024-01-01T00:00:00Z",
            time_max="2024-01-31T23:59:59Z",
            time_zone="America/Denver",
        )
        parsed = json.loads(result)
        assert "primary" in parsed["calendars"]
        assert "other@example.com" in parsed["calendars"]
        call_kwargs = mock_client.freebusy.query.call_args.kwargs
        assert call_kwargs["time_zone"] == "America/Denver"

    def test_query_freebusy_error(self, mock_client):
        from calendar_mcp.tools.freebusy import query_freebusy

        mock_client.freebusy.query.side_effect = RuntimeError("API error")
        result = query_freebusy(
            calendar_ids='["primary"]',
            time_min="2024-01-01T00:00:00Z",
            time_max="2024-01-31T23:59:59Z",
        )
        parsed = json.loads(result)
        assert parsed["error"] is True
        assert "API error" in parsed["message"]

    def test_query_freebusy_invalid_json(self, mock_client):
        from calendar_mcp.tools.freebusy import query_freebusy

        result = query_freebusy(
            calendar_ids="{bad json[",
            time_min="2024-01-01T00:00:00Z",
            time_max="2024-01-31T23:59:59Z",
        )
        parsed = json.loads(result)
        assert parsed["error"] is True
        assert "Invalid JSON" in parsed["message"]
