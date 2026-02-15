"""Tests for calendar tools.

These tests mock the GCalClient so no real API calls are made.
"""

from __future__ import annotations

import json

from gcal_sdk.models import Calendar


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_calendar(**overrides):
    """Create a mock Calendar with sensible defaults."""
    defaults = {
        "id": "cal-1",
        "summary": "My Calendar",
        "timeZone": "America/Denver",
        "primary": True,
        "accessRole": "owner",
        "etag": '"xyz789"',
        "kind": "calendar#calendarListEntry",
    }
    defaults.update(overrides)
    return Calendar.from_api_response(defaults)


# ---------------------------------------------------------------------------
# list_calendars
# ---------------------------------------------------------------------------


class TestListCalendars:
    def test_list_calendars_default(self, mock_client):
        from gcal_mcp.tools.calendars import list_calendars

        mock_client.calendars.list.return_value = [_make_mock_calendar()]
        result = list_calendars()
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["id"] == "cal-1"
        mock_client.calendars.list.assert_called_once_with(
            show_deleted=False,
            show_hidden=False,
            max_results=100,
        )

    def test_list_calendars_with_options(self, mock_client):
        from gcal_mcp.tools.calendars import list_calendars

        mock_client.calendars.list.return_value = []
        result = list_calendars(show_deleted=True, show_hidden=True, max_results=50)
        parsed = json.loads(result)
        assert parsed == []
        mock_client.calendars.list.assert_called_once_with(
            show_deleted=True,
            show_hidden=True,
            max_results=50,
        )


# ---------------------------------------------------------------------------
# get_calendar
# ---------------------------------------------------------------------------


class TestGetCalendar:
    def test_get_calendar(self, mock_client):
        from gcal_mcp.tools.calendars import get_calendar

        mock_client.calendars.get.return_value = _make_mock_calendar()
        result = get_calendar("primary")
        parsed = json.loads(result)
        assert parsed["id"] == "cal-1"
        mock_client.calendars.get.assert_called_once_with("primary")

    def test_get_calendar_default(self, mock_client):
        from gcal_mcp.tools.calendars import get_calendar

        mock_client.calendars.get.return_value = _make_mock_calendar()
        result = get_calendar()
        parsed = json.loads(result)
        assert parsed["id"] == "cal-1"
        mock_client.calendars.get.assert_called_once_with("primary")


# ---------------------------------------------------------------------------
# create_calendar
# ---------------------------------------------------------------------------


class TestCreateCalendar:
    def test_create_calendar_basic(self, mock_client):
        from gcal_mcp.tools.calendars import create_calendar

        mock_client.calendars.create.return_value = _make_mock_calendar(
            id="new-cal", summary="Work"
        )
        result = create_calendar(summary="Work")
        parsed = json.loads(result)
        assert parsed["id"] == "new-cal"
        assert parsed["summary"] == "Work"
        mock_client.calendars.create.assert_called_once_with(
            "Work",
            description=None,
            time_zone=None,
            location=None,
        )

    def test_create_calendar_full(self, mock_client):
        from gcal_mcp.tools.calendars import create_calendar

        mock_client.calendars.create.return_value = _make_mock_calendar(id="new-cal")
        result = create_calendar(
            summary="Projects",
            description="Project tracking calendar",
            time_zone="America/Denver",
            location="Denver, CO",
        )
        parsed = json.loads(result)
        assert parsed["id"] == "new-cal"
        mock_client.calendars.create.assert_called_once_with(
            "Projects",
            description="Project tracking calendar",
            time_zone="America/Denver",
            location="Denver, CO",
        )


# ---------------------------------------------------------------------------
# delete_calendar
# ---------------------------------------------------------------------------


class TestDeleteCalendar:
    def test_delete_calendar(self, mock_client):
        from gcal_mcp.tools.calendars import delete_calendar

        mock_client.calendars.delete.return_value = None
        result = delete_calendar("cal-to-delete")
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["deleted"] == "cal-to-delete"
        mock_client.calendars.delete.assert_called_once_with("cal-to-delete")


# ---------------------------------------------------------------------------
# clear_calendar
# ---------------------------------------------------------------------------


class TestClearCalendar:
    def test_clear_calendar(self, mock_client):
        from gcal_mcp.tools.calendars import clear_calendar

        mock_client.calendars.clear.return_value = None
        result = clear_calendar("primary")
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["cleared"] == "primary"
        mock_client.calendars.clear.assert_called_once_with("primary")

    def test_clear_calendar_default(self, mock_client):
        from gcal_mcp.tools.calendars import clear_calendar

        mock_client.calendars.clear.return_value = None
        result = clear_calendar()
        parsed = json.loads(result)
        assert parsed["success"] is True
        mock_client.calendars.clear.assert_called_once_with("primary")


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestCalendarErrorHandling:
    def test_sdk_exception(self, mock_client):
        from gcal_mcp.tools.calendars import get_calendar

        mock_client.calendars.get.side_effect = RuntimeError("Auth expired")
        result = get_calendar("primary")
        parsed = json.loads(result)
        assert parsed["error"] is True
        assert "Auth expired" in parsed["message"]
