"""Shared test fixtures for gcal-mcp tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_client():
    """Patch get_client() to return a MagicMock for every test."""
    client = MagicMock()
    with patch("gcal_mcp.server._client", None):
        with patch("gcal_mcp.server.GCalClient", return_value=client):
            import gcal_mcp.server as srv
            srv._client = None
            yield client
            srv._client = None
