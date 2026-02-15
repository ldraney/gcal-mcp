"""Tool registration -- imports every tool module so @mcp.tool() decorators fire."""

from __future__ import annotations


def register_all_tools() -> None:
    """Import all tool modules, which register tools via the module-level @mcp.tool() decorators."""
    from . import events  # noqa: F401
    from . import calendars  # noqa: F401
    from . import freebusy  # noqa: F401
