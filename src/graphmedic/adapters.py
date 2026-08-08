from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Protocol

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .models import AssetSnapshot, ProposedAction
from .policy import REVIEW_TAG


DEMO_TAG = "GraphMedicDemo"
DEMO_PLATFORM = "graphmedic_demo"
REVIEW_TAG_URN = f"urn:li:tag:{REVIEW_TAG}"


class CatalogAdapter(Protocol):
    tool_evidence: list[dict[str, Any]]

    async def scan_assets(self) -> list[AssetSnapshot]: ...

    async def apply_action(self, action: ProposedAction) -> dict[str, Any]: ...


def _json_result(result: Any) -> Any:
    if getattr(result, "isError", False):
        raise RuntimeError("DataHub MCP tool returned an error")
    for block in getattr(result, "content", []):
        text = getattr(block, "text", None)
        if text:
            return json.loads(text)
    raise RuntimeError("DataHub MCP tool returned no JSON content")


def _tag_names(entity: dict[str, Any]) -> tuple[str, ...]:
    tags = entity.get("tags", {}).get("tags", [])
    names = []
    for association in tags:
        tag = association.get("tag", {})
        name = tag.get("properties", {}).get("name") or tag.get("urn", "").rsplit(":", 1)[-1]
        if name:
            names.append(name)
    return tuple(names)


def _owners(entity: dict[str, Any]) -> tuple[str, ...]:
    values = []
    for association in entity.get("ownership", {}).get("owners", []):
        urn = association.get("owner", {}).get("urn")
        if urn:
            values.append(urn)
    return tuple(values)


def _custom_properties(entity: dict[str, Any]) -> dict[str, str]:
    return {
        item.get("key", ""): item.get("value", "")
        for item in entity.get("properties", {}).get("customProperties", [])
    }


def _is_allowlisted(entity: dict[str, Any]) -> bool:
    return (
        DEMO_PLATFORM in entity.get("urn", "")
        and DEMO_TAG in _tag_names(entity)
        and _custom_properties(entity).get("data_classification") == "SYNTHETIC"
    )


class DataHubMCPAdapter:
    """Official MCP client with a deny-by-default synthetic-data boundary."""

    def __init__(self, gms_url: str = "http://127.0.0.1:18080") -> None:
        self.gms_url = gms_url
        self.tool_evidence: list[dict[str, Any]] = []

    def _parameters(self) -> StdioServerParameters:
        configured = os.environ.get("DATAHUB_MCP_COMMAND")
        if configured:
            command = configured
        else:
            executable = Path(os.sys.executable).with_name("mcp-server-datahub.exe")
            command = str(executable)
        environment = os.environ.copy()
        environment.update(
            {
                "DATAHUB_GMS_URL": self.gms_url,
                "TOOLS_IS_MUTATION_ENABLED": "true",
                "DATAHUB_MCP_DOCUMENT_TOOLS_DISABLED": "true",
            }
        )
        return StdioServerParameters(command=command, env=environment)

    async def _call(self, session: ClientSession, name: str, arguments: dict[str, Any]) -> Any:
        started = time.perf_counter()
        result = await session.call_tool(name, arguments)
        payload = _json_result(result)
        elapsed = round((time.perf_counter() - started) * 1000)
        self.tool_evidence.append(
            {
                "tool": name,
                "argument_keys": sorted(arguments),
                "duration_ms": elapsed,
                "status": "verified",
            }
        )
        return payload

    async def scan_assets(self) -> list[AssetSnapshot]:
        self.tool_evidence = []
        async with stdio_client(self._parameters()) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                search = await self._call(
                    session, "search", {"query": DEMO_PLATFORM, "num_results": 20}
                )
                urns = [
                    item.get("entity", {}).get("urn", "")
                    for item in search.get("searchResults", [])
                ]
                urns = sorted(
                    urn for urn in urns if urn.startswith("urn:li:dataset:") and DEMO_PLATFORM in urn
                )
                entities = await self._call(session, "get_entities", {"urns": urns})
                allowed = [entity for entity in entities if _is_allowlisted(entity)]
                assets = []
                for entity in allowed:
                    urn = entity["urn"]
                    upstream = await self._call(
                        session,
                        "get_lineage",
                        {"urn": urn, "upstream": True, "max_hops": 1, "max_results": 30},
                    )
                    downstream = await self._call(
                        session,
                        "get_lineage",
                        {"urn": urn, "upstream": False, "max_hops": 1, "max_results": 30},
                    )
                    upstream_entities = [
                        item.get("entity", {})
                        for item in upstream.get("upstreams", {}).get("searchResults", [])
                    ]
                    downstream_urns = tuple(
                        item.get("entity", {}).get("urn", "")
                        for item in downstream.get("downstreams", {}).get("searchResults", [])
                        if DEMO_PLATFORM in item.get("entity", {}).get("urn", "")
                    )
                    properties = entity.get("properties", {})
                    assets.append(
                        AssetSnapshot(
                            urn=urn,
                            name=entity.get("name") or properties.get("name") or urn,
                            platform=entity.get("platform", {}).get("name", DEMO_PLATFORM),
                            description=properties.get("description") or "",
                            owners=_owners(entity),
                            tags=_tag_names(entity),
                            downstream=downstream_urns,
                            has_deprecated_upstream=any(
                                upstream_entity.get("deprecation", {}).get("deprecated") is True
                                for upstream_entity in upstream_entities
                            ),
                        )
                    )
        return assets

    async def apply_action(self, action: ProposedAction) -> dict[str, Any]:
        if DEMO_PLATFORM not in action.urn:
            raise PermissionError("Mutation rejected: URN is outside the synthetic demo namespace")
        if action.kind == "add_tag" and action.value != REVIEW_TAG:
            raise PermissionError("Mutation rejected: tag is not allowlisted")
        if action.kind == "append_description" and not action.value.startswith("GraphMedic review:"):
            raise PermissionError("Mutation rejected: description is not an approved GraphMedic note")

        self.tool_evidence = []
        async with stdio_client(self._parameters()) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                before = await self._call(session, "get_entities", {"urns": [action.urn]})
                if len(before) != 1 or not _is_allowlisted(before[0]):
                    raise PermissionError("Mutation rejected: asset lacks all synthetic opt-in markers")
                if action.kind == "add_tag":
                    await self._call(
                        session,
                        "add_tags",
                        {"entity_urns": [action.urn], "tag_urns": [REVIEW_TAG_URN]},
                    )
                elif action.kind == "append_description":
                    await self._call(
                        session,
                        "update_description",
                        {
                            "entity_urn": action.urn,
                            "description": action.value,
                            "operation": "append",
                        },
                    )
                else:
                    raise PermissionError("Mutation rejected: operation is not allowlisted")
                after = await self._call(session, "get_entities", {"urns": [action.urn]})
                if len(after) != 1 or not _is_allowlisted(after[0]):
                    raise RuntimeError("Post-write verification failed")
        return {"status": "applied_and_verified", "action": action.to_dict(), "tool_evidence": self.tool_evidence}


class FixtureAdapter:
    """Small offline adapter used by automated tests and reviewer-safe fallback."""

    def __init__(self) -> None:
        self.tool_evidence: list[dict[str, Any]] = []
        self.assets = [
            AssetSnapshot(
                urn="urn:li:dataset:(urn:li:dataPlatform:graphmedic_demo,demo.orders,PROD)",
                name="Orders",
                platform=DEMO_PLATFORM,
                tags=(DEMO_TAG,),
                downstream=("urn:li:dataset:(urn:li:dataPlatform:graphmedic_demo,demo.revenue,PROD)",),
                has_deprecated_upstream=True,
            )
        ]

    async def scan_assets(self) -> list[AssetSnapshot]:
        self.tool_evidence = [
            {"tool": "fixture_search", "argument_keys": ["synthetic_only"], "duration_ms": 1, "status": "verified"}
        ]
        return list(self.assets)

    async def apply_action(self, action: ProposedAction) -> dict[str, Any]:
        if DEMO_PLATFORM not in action.urn:
            raise PermissionError("Fixture mutation rejected")
        self.tool_evidence = [{"tool": "fixture_write", "argument_keys": ["approved_action"], "duration_ms": 1, "status": "verified"}]
        return {"status": "applied_and_verified", "action": action.to_dict(), "tool_evidence": self.tool_evidence}
