# calendar-mcp

MCP server for Google Calendar, built on [gcal-sdk](https://github.com/ldraney/gcal-sdk).

## Install

```bash
pip install calendar-mcp
```

## Run

```bash
calendar-mcp
# or
python -m calendar_mcp
```

## Claude Code config

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "calendar": {
      "command": "calendar-mcp"
    }
  }
}
```

## Prerequisites

Google OAuth credentials must be set up at `~/secrets/google-oauth/`:
- `credentials.json` -- OAuth client credentials
- `token.json` -- stored OAuth token

See the [Google OAuth Setup Guide](docs/google-oauth-setup.html) for details.

## Available tools

### Events
- `list_events` -- List events from a calendar
- `get_event` -- Get a single event by ID
- `create_event` -- Create a new event
- `update_event` -- Full update (PUT) of an event
- `patch_event` -- Partial update (PATCH) of an event
- `delete_event` -- Delete an event
- `move_event` -- Move an event to another calendar
- `list_event_instances` -- List instances of a recurring event

### Calendars
- `list_calendars` -- List all calendars
- `get_calendar` -- Get details about a calendar
- `create_calendar` -- Create a new secondary calendar
- `delete_calendar` -- Delete a secondary calendar
- `clear_calendar` -- Clear all events from a calendar

### FreeBusy
- `query_freebusy` -- Query free/busy info for calendars
