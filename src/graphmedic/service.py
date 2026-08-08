from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .adapters import CatalogAdapter
from .models import Finding, ScanReport
from .policy import analyze_assets


class GraphMedicService:
    def __init__(self, adapter: CatalogAdapter, audit_path: Path) -> None:
        self.adapter = adapter
        self.audit_path = audit_path
        self._findings: dict[str, Finding] = {}

    async def scan(self) -> ScanReport:
        assets = await self.adapter.scan_assets()
        findings = analyze_assets(assets)
        self._findings = {finding.id: finding for finding in findings}
        return ScanReport(
            mode=type(self.adapter).__name__,
            synthetic_data_only=True,
            assets=assets,
            findings=findings,
            tool_evidence=list(self.adapter.tool_evidence),
        )

    async def apply(self, finding_id: str, action_kind: str, approved: bool) -> dict[str, object]:
        if approved is not True:
            raise PermissionError("Explicit approval is required")
        finding = self._findings.get(finding_id)
        if finding is None:
            raise KeyError("Finding is stale or unknown; run a fresh scan")
        action = next((item for item in finding.actions if item.kind == action_kind), None)
        if action is None:
            raise KeyError("Action is not part of the current reviewed proposal")
        result = await self.adapter.apply_action(action)
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "finding_id": finding_id,
            "action": action.to_dict(),
            "result": result["status"],
            "synthetic_data_only": True,
        }
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        return {"event": event, "tool_evidence": result["tool_evidence"]}

    def audit(self) -> list[dict[str, object]]:
        if not self.audit_path.exists():
            return []
        return [json.loads(line) for line in self.audit_path.read_text(encoding="utf-8").splitlines() if line]
