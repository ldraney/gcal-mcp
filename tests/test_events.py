"""Tests for event tools.

These tests mock the GCalClient so no real API calls are made.
They verify that:
  - SDK methods receive the expected arguments
  - Successful responses are returned as JSON strings
  - Datetime strings are parsed correctly
  - Errors are caught and formatted properly
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from gcal_sdk.models import Event, EventDateTime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_event(**overrides):
    """Create a mock Event with sensible defaults."""
    defaults = {
        "id": "event-1",
        "summary": "Test Event",
        "start": EventDateTime(date_time=datetime(2024, 6, 15, 10, 0, tzinfo=timezone.utc)),
        "end": EventDateTime(date_time=datetime(2024, 6, 15, 11, 0, tzinfo=timezone.utc)),
        "status": "confirmed",
        "etag": '"abc123"',
        "kind": "calendar#event",
        "iCalUID": "event-1@google.com",
        "sequence": 0,
        "reminders": {"useDefault": True},
    }
    defaults.update(overrides)
    return Event(**defaults)


# ---------------------------------------------------------------------------
# list_events
# ---------------------------------------------------------------------------


class TestListEvents:
    def test_list_events_default(self, mock_client):
        from gcal_mcp.tools.events import list_events

        mock_client.events.list.return_value = [_make_mock_event()]
        result = list_events()
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["id"] == "event-1"
        mock_client.events.list.assert_called_once_with(
            "primary",
            time_min=None,
            time_max=None,
            max_results=25,
            q=None,
            single_events=True,
            order_by="startTime",
            show_deleted=False,
            page_token=None,
        )

    def test_list_events_with_time_range(self, mock_client):
        from gcal_mcp.tools.events import list_events

        mock_client.events.list.return_value = []
        result = list_events(
            time_min="2024-01-01T00:00:00Z",
            time_max="2024-12-31T23:59:59Z",
            max_results=10,
        )
        parsed = json.loads(result)
        assert parsed == []
        call_kwargs = mock_client.events.list.call_args
        # time_min and time_max should be parsed to datetime objects
        assert call_kwargs.kwargs["time_min"] == datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert call_kwargs.kwargs["time_max"] == datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    def test_list_events_with_search(self, mock_client):
        from gcal_mcp.tools.events import list_events

        mock_client.events.list.return_value = [_make_mock_event(summary="Meeting")]
        result = list_events(q="meeting")
        parsed = json.loads(result)
        assert len(parsed) == 1
        mock_client.events.list.assert_called_once_with(
            "primary",
            time_min=None,
            time_max=None,
            max_results=25,
            q="meeting",
            single_events=True,
            order_by="startTime",
            show_deleted=False,
            page_token=None,
        )


# ---------------------------------------------------------------------------
# get_event
# ---------------------------------------------------------------------------


class TestGetEvent:
    def test_get_event(self, mock_client):
        from gcal_mcp.tools.events import get_event

        mock_client.events.get.return_value = _make_mock_event()
        result = get_event("primary", "event-1")
        parsed = json.loads(result)
        assert parsed["id"] == "event-1"
        mock_client.events.get.assert_called_once_with("primary", "event-1")


# ---------------------------------------------------------------------------
# create_event
# ---------------------------------------------------------------------------


class TestCreateEvent:
    def test_create_event_basic(self, mock_client):
        from gcal_mcp.tools.events import create_event

        mock_client.events.create.return_value = _make_mock_event(id="new-event")
        result = create_event(
            summary="New Meeting",
            start="2024-06-15T10:00:00Z",
            end="2024-06-15T11:00:00Z",
        )
        parsed = json.loads(result)
        assert parsed["id"] == "new-event"
        call_kwargs = mock_client.events.create.call_args
        assert call_kwargs.args[0] == "primary"
        assert call_kwargs.kwargs["summary"] == "New Meeting"
        assert call_kwargs.kwargs["start"] == datetime(2024, 6, 15, 10, 0, tzinfo=timezone.utc)
        assert call_kwargs.kwargs["end"] == datetime(2024, 6, 15, 11, 0, tzinfo=timezone.utc)

    def test_create_event_with_attendees_json(self, mock_client):
        from gcal_mcp.tools.events import create_event

        mock_client.events.create.return_value = _make_mock_event()
        result = create_event(
            summary="Team Sync",
            start="2024-06-15T10:00:00Z",
            end="2024-06-15T11:00:00Z",
            attendees='["alice@example.com", "bob@example.com"]',
        )
        parsed = json.loads(result)
        assert parsed["id"] == "event-1"
        call_kwargs = mock_client.events.create.call_args.kwargs
        assert call_kwargs["attendees"] == ["alice@example.com", "bob@example.com"]

    def test_create_event_with_attendees_list(self, mock_client):
        from gcal_mcp.tools.events import create_event

        mock_client.events.create.return_value = _make_mock_event()
        result = create_event(
            summary="Team Sync",
            start="2024-06-15T10:00:00Z",
            end="2024-06-15T11:00:00Z",
            attendees=["alice@example.com", "bob@example.com"],
        )
        parsed = json.loads(result)
        assert parsed["id"] == "event-1"
        call_kwargs = mock_client.events.create.call_args.kwargs
        assert call_kwargs["attendees"] == ["alice@example.com", "bob@example.com"]

    def test_create_event_with_all_fields(self, mock_client):
        from gcal_mcp.tools.events import create_event

        mock_client.events.create.return_value = _make_mock_event()
        result = create_event(
            summary="Offsite",
            start="2024-06-15T10:00:00-06:00",
            end="2024-06-15T11:00:00-06:00",
            description="Annual offsite meeting",
            location="Denver, CO",
            time_zone="America/Denver",
            calendar_id="work-calendar",
        )
        parsed = json.loads(result)
        assert parsed["id"] == "event-1"
        call_kwargs = mock_client.events.create.call_args
        assert call_kwargs.args[0] == "work-calendar"
        assert call_kwargs.kwargs["description"] == "Annual offsite meeting"
        assert call_kwargs.kwargs["location"] == "Denver, CO"
        assert call_kwargs.kwargs["time_zone"] == "America/Denver"


# ---------------------------------------------------------------------------
# update_event
# ---------------------------------------------------------------------------


class TestUpdateEvent:
    def test_update_event(self, mock_client):
        from gcal_mcp.tools.events import update_event

        mock_client.events.update.return_value = _make_mock_event(summary="Updated")
        body = json.dumps({"summary": "Updated", "start": {"dateTime": "2024-06-15T10:00:00Z"}})
        result = update_event("primary", "event-1", body=body)
        parsed = json.loads(result)
        assert parsed["summary"] == "Updated"
        mock_client.events.update.assert_called_once_with(
            "primary", "event-1",
            body={"summary": "Updated", "start": {"dateTime": "2024-06-15T10:00:00Z"}},
        )

    def test_update_event_dict_body(self, mock_client):
        from gcal_mcp.tools.events import update_event

        mock_client.events.update.return_value = _make_mock_event(summary="Updated")
        body = {"summary": "Updated"}
        result = update_event("primary", "event-1", body=body)
        parsed = json.loads(result)
        assert parsed["summary"] == "Updated"
        mock_client.events.update.assert_called_once_with(
            "primary", "event-1", body={"summary": "Updated"},
        )


# ---------------------------------------------------------------------------
# patch_event
# ---------------------------------------------------------------------------


class TestPatchEvent:
    def test_patch_event_summary(self, mock_client):
        from gcal_mcp.tools.events import patch_event

        mock_client.events.patch.return_value = _make_mock_event(summary="Patched")
        result = patch_event("primary", "event-1", summary="Patched")
        parsed = json.loads(result)
        assert parsed["summary"] == "Patched"
        call_kwargs = mock_client.events.patch.call_args.kwargs
        assert call_kwargs["summary"] == "Patched"

    def test_patch_event_time(self, mock_client):
        from gcal_mcp.tools.events import patch_event

        mock_client.events.patch.return_value = _make_mock_event()
        result = patch_event(
            "primary", "event-1",
            start="2024-06-20T09:00:00Z",
            end="2024-06-20T10:00:00Z",
        )
        parsed = json.loads(result)
        assert parsed["id"] == "event-1"
        call_kwargs = mock_client.events.patch.call_args.kwargs
        assert call_kwargs["start"] == datetime(2024, 6, 20, 9, 0, tzinfo=timezone.utc)
        assert call_kwargs["end"] == datetime(2024, 6, 20, 10, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# delete_event
# ---------------------------------------------------------------------------


class TestDeleteEvent:
    def test_delete_event(self, mock_client):
        from gcal_mcp.tools.events import delete_event

        mock_client.events.delete.return_value = None
        result = delete_event("primary", "event-1")
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["deleted"] == "event-1"
        mock_client.events.delete.assert_called_once_with(
            "primary", "event-1", send_updates=None,
        )

    def test_delete_event_with_notifications(self, mock_client):
        from gcal_mcp.tools.events import delete_event

        mock_client.events.delete.return_value = None
        result = delete_event("primary", "event-1", send_updates="all")
        parsed = json.loads(result)
        assert parsed["success"] is True
        mock_client.events.delete.assert_called_once_with(
            "primary", "event-1", send_updates="all",
        )


# ---------------------------------------------------------------------------
# move_event
# ---------------------------------------------------------------------------


class TestMoveEvent:
    def test_move_event(self, mock_client):
        from gcal_mcp.tools.events import move_event

        mock_client.events.move.return_value = _make_mock_event()
        result = move_event("primary", "event-1", "other-calendar")
        parsed = json.loads(result)
        assert parsed["id"] == "event-1"
        mock_client.events.move.assert_called_once_with(
            "primary", "event-1", "other-calendar",
        )


# ---------------------------------------------------------------------------
# list_event_instances
# ---------------------------------------------------------------------------


class TestListEventInstances:
    def test_list_instances(self, mock_client):
        from gcal_mcp.tools.events import list_event_instances

        mock_client.events.instances.return_value = [
            _make_mock_event(id="instance-1"),
            _make_mock_event(id="instance-2"),
        ]
        result = list_event_instances("primary", "recurring-event-1")
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["id"] == "instance-1"
        mock_client.events.instances.assert_called_once_with(
            "primary", "recurring-event-1",
            time_min=None,
            time_max=None,
            max_results=25,
        )

    def test_list_instances_with_time_range(self, mock_client):
        from gcal_mcp.tools.events import list_event_instances

        mock_client.events.instances.return_value = []
        result = list_event_instances(
            "primary", "recurring-event-1",
            time_min="2024-01-01T00:00:00Z",
            time_max="2024-06-30T23:59:59Z",
            max_results=10,
        )
        parsed = json.loads(result)
        assert parsed == []
        call_kwargs = mock_client.events.instances.call_args.kwargs
        assert call_kwargs["time_min"] == datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert call_kwargs["max_results"] == 10


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestEventErrorHandling:
    def test_sdk_exception(self, mock_client):
        from gcal_mcp.tools.events import get_event

        mock_client.events.get.side_effect = RuntimeError("Connection failed")
        result = get_event("primary", "event-1")
        parsed = json.loads(result)
        assert parsed["error"] is True
        assert "Connection failed" in parsed["message"]

    def test_invalid_json_attendees(self, mock_client):
        from gcal_mcp.tools.events import create_event

        result = create_event(
            summary="Bad",
            start="2024-06-15T10:00:00Z",
            end="2024-06-15T11:00:00Z",
            attendees="{not valid json[",
        )
        parsed = json.loads(result)
        assert parsed["error"] is True
        assert "Invalid JSON" in parsed["message"]
