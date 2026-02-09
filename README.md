# calendar-mcp

Google Calendar MCP server for Claude Code.

## What is this?

An MCP (Model Context Protocol) server that gives Claude Code direct access to Google Calendar. Create, read, update, and delete calendar events through natural conversation.

## Architecture

Part of the **Claude Agent** execution layer:

```
OpenClaw Commander (orchestration)
  └── Claude Agent: Calendar Manager
        ├── MCP: calendar-mcp (this repo)
        ├── Skills: /add-event, /daily-agenda, /upcoming
        └── SOP: Calendar Event Management
```

## Status

**Planning** — Setting up Google OAuth and MCP server.

## Setup

See the [Google OAuth Setup Guide](docs/google-oauth-setup.md) (coming soon).
