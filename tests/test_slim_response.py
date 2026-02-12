"""Tests for _slim_response -- verifies Calendar API noise stripping."""

from __future__ import annotations

from calendar_mcp.server import _slim_response


class TestAlwaysStrippedKeys:
    def test_etag_stripped(self):
        data = {"id": "event-1", "etag": '"abc123"', "summary": "Test"}
        result = _slim_response(data)
        assert "etag" not in result
        assert result["summary"] == "Test"

    def test_kind_stripped(self):
        data = {"id": "event-1", "kind": "calendar#event", "summary": "Test"}
        result = _slim_response(data)
        assert "kind" not in result
        assert result["summary"] == "Test"

    def test_both_stripped(self):
        data = {"id": "event-1", "etag": '"xyz"', "kind": "calendar#event", "summary": "Test"}
        result = _slim_response(data)
        assert "etag" not in result
        assert "kind" not in result
        assert result["id"] == "event-1"


class TestNullStripping:
    def test_null_values_stripped(self):
        data = {"id": "event-1", "description": None, "location": None, "summary": "Test"}
        result = _slim_response(data)
        assert "description" not in result
        assert "location" not in result
        assert result["summary"] == "Test"

    def test_non_null_values_kept(self):
        data = {"id": "event-1", "description": "A meeting", "summary": "Test"}
        result = _slim_response(data)
        assert result["description"] == "A meeting"


class TestEmptyValueStripping:
    def test_empty_string_stripped(self):
        data = {"id": "event-1", "description": "", "summary": "Test"}
        result = _slim_response(data)
        assert "description" not in result

    def test_empty_list_stripped(self):
        data = {"id": "event-1", "attendees": [], "summary": "Test"}
        result = _slim_response(data)
        assert "attendees" not in result

    def test_non_empty_list_kept(self):
        data = {"id": "event-1", "attendees": [{"email": "a@b.com"}]}
        result = _slim_response(data)
        assert len(result["attendees"]) == 1


class TestICalUIDStripping:
    def test_icaluid_stripped(self):
        data = {"id": "event-1", "iCalUID": "event-1@google.com", "summary": "Test"}
        result = _slim_response(data)
        assert "iCalUID" not in result
        assert result["id"] == "event-1"


class TestRemindersStripping:
    def test_default_reminders_stripped(self):
        data = {"id": "event-1", "reminders": {"useDefault": True}, "summary": "Test"}
        result = _slim_response(data)
        assert "reminders" not in result

    def test_custom_reminders_kept(self):
        data = {
            "id": "event-1",
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 10}],
            },
        }
        result = _slim_response(data)
        assert "reminders" in result
        assert result["reminders"]["overrides"][0]["minutes"] == 10

    def test_use_default_pydantic_style_stripped(self):
        """Handle the case where pydantic serializes as use_default instead of useDefault."""
        data = {"id": "event-1", "reminders": {"use_default": True}, "summary": "Test"}
        result = _slim_response(data)
        assert "reminders" not in result


class TestSequenceStripping:
    def test_sequence_zero_stripped(self):
        data = {"id": "event-1", "sequence": 0, "summary": "Test"}
        result = _slim_response(data)
        assert "sequence" not in result

    def test_sequence_nonzero_kept(self):
        data = {"id": "event-1", "sequence": 3, "summary": "Test"}
        result = _slim_response(data)
        assert result["sequence"] == 3


class TestRecursiveSlimming:
    def test_nested_dict_slimmed(self):
        data = {
            "id": "event-1",
            "start": {
                "dateTime": "2024-06-15T10:00:00Z",
                "timeZone": "UTC",
                "etag": "should-strip",
            },
        }
        result = _slim_response(data)
        assert "etag" not in result["start"]
        assert result["start"]["dateTime"] == "2024-06-15T10:00:00Z"

    def test_list_of_dicts_slimmed(self):
        data = [
            {"id": "e1", "etag": '"a"', "kind": "calendar#event", "summary": "One"},
            {"id": "e2", "etag": '"b"', "kind": "calendar#event", "summary": "Two"},
        ]
        result = _slim_response(data)
        assert len(result) == 2
        for item in result:
            assert "etag" not in item
            assert "kind" not in item


class TestEdgeCases:
    def test_empty_dict(self):
        assert _slim_response({}) == {}

    def test_empty_list(self):
        assert _slim_response([]) == []

    def test_primitive_passthrough(self):
        assert _slim_response("hello") == "hello"
        assert _slim_response(42) == 42
        assert _slim_response(True) is True
        assert _slim_response(None) is None


class TestRealisticEventSlimming:
    """A realistic event slimmed to verify end-to-end behavior."""

    def test_full_event_slimmed(self):
        raw = {
            "id": "abc123",
            "etag": '"3456789"',
            "kind": "calendar#event",
            "summary": "Team Standup",
            "description": "Daily standup meeting",
            "location": None,
            "start": {"dateTime": "2024-06-15T09:00:00-06:00", "timeZone": "America/Denver"},
            "end": {"dateTime": "2024-06-15T09:15:00-06:00", "timeZone": "America/Denver"},
            "status": "confirmed",
            "htmlLink": "https://calendar.google.com/event?eid=abc123",
            "created": "2024-01-01T00:00:00.000Z",
            "updated": "2024-06-14T20:00:00.000Z",
            "creator": {"email": "user@example.com"},
            "organizer": {"email": "user@example.com"},
            "iCalUID": "abc123@google.com",
            "sequence": 0,
            "reminders": {"useDefault": True},
            "attendees": [],
            "colorId": None,
        }

        result = _slim_response(raw)

        # Stripped fields
        assert "etag" not in result
        assert "kind" not in result
        assert "iCalUID" not in result
        assert "sequence" not in result
        assert "reminders" not in result
        assert "location" not in result  # null
        assert "attendees" not in result  # empty list
        assert "colorId" not in result  # null

        # Kept fields
        assert result["id"] == "abc123"
        assert result["summary"] == "Team Standup"
        assert result["description"] == "Daily standup meeting"
        assert result["status"] == "confirmed"
        assert result["htmlLink"] == "https://calendar.google.com/event?eid=abc123"
        assert result["creator"] == {"email": "user@example.com"}
        assert result["organizer"] == {"email": "user@example.com"}
        assert result["start"]["dateTime"] == "2024-06-15T09:00:00-06:00"
