from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    executable = Path(__file__).parents[1] / ".venv" / "Scripts" / "mcp-server-datahub.exe"
    environment = os.environ.copy()
    environment.update(
        {
            "DATAHUB_GMS_URL": "http://127.0.0.1:18080",
            "TOOLS_IS_MUTATION_ENABLED": "true",
            "DATAHUB_MCP_DOCUMENT_TOOLS_DISABLED": "true",
        }
    )
    parameters = StdioServerParameters(command=str(executable), env=environment)
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = await session.list_tools()
            wanted = {"search", "get_entities", "get_lineage", "add_tags", "update_description"}
            selected = {
                tool.name: tool.inputSchema
                for tool in tools.tools
                if tool.name in wanted
            }
            print(json.dumps(selected, indent=2, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
