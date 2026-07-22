"""
Throwaway verification script — Phase 3.

Run from the repo root after setting up your .env:

    cd backend
    python ../scripts/test_mcp.py

Expected output:
    Connecting to MCP filesystem server...
    Discovered N tool(s): read_file, write_file, list_directory, ...
    Calling list_directory on demo-workspace...
    README.md  notes.txt  sample-data.csv
    Calling read_file on notes.txt...
    Project: ChatAgent Demo ...
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import get_settings
from app.infrastructure.mcp.client import MCPToolClient


async def main() -> None:
    settings = get_settings()
    root = (Path(__file__).parent.parent / settings.mcp_filesystem_root).resolve()

    print(f"Connecting to MCP filesystem server (root: {root})\n")

    async with MCPToolClient(root) as client:
        # 1 — list tools
        tools = await client.list_tools()
        print(f"Discovered {len(tools)} tool(s):")
        for t in tools:
            print(f"  {t.name}: {t.description[:60]}...")

        # 2 — list the demo-workspace directory
        print(f"\nCalling list_directory on {root} ...")
        list_result = await client.call_tool("list_directory", {"path": str(root)})
        print(f"  is_error: {list_result.is_error}")
        print(f"  content:\n{list_result.content}\n")

        # 3 — read notes.txt
        notes_path = str(root / "notes.txt")
        print(f"Calling read_file on {notes_path} ...")
        read_result = await client.call_tool("read_file", {"path": notes_path})
        print(f"  is_error: {read_result.is_error}")
        print(f"  content:\n{read_result.content}")


if __name__ == "__main__":
    asyncio.run(main())
