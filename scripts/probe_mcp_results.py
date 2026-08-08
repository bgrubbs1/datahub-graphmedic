from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def content(result: object) -> object:
    blocks = getattr(result, "content", [])
    return [getattr(block, "text", str(block)) for block in blocks]


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
            search = await session.call_tool("search", {"query": "graphmedic_demo", "num_results": 10})
            print("SEARCH")
            print(json.dumps(content(search), indent=2))
            urn = "urn:li:dataset:(urn:li:dataPlatform:graphmedic_demo,demo_ops.orders_clean,PROD)"
            entity = await session.call_tool("get_entities", {"urns": [urn]})
            print("ENTITY")
            print(json.dumps(content(entity), indent=2))
            for upstream in (True, False):
                lineage = await session.call_tool(
                    "get_lineage", {"urn": urn, "upstream": upstream, "max_hops": 1, "max_results": 20}
                )
                print(f"LINEAGE upstream={upstream}")
                print(json.dumps(content(lineage), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
