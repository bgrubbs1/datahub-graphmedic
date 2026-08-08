from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


Severity = Literal["critical", "high", "medium", "low"]
ActionKind = Literal["add_tag", "append_description"]


@dataclass(frozen=True)
class AssetSnapshot:
    urn: str
    name: str
    platform: str
    description: str = ""
    owners: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    downstream: tuple[str, ...] = ()
    has_deprecated_upstream: bool = False

    @property
    def is_demo_asset(self) -> bool:
        return "graphmedic_demo" in self.urn and "GraphMedicDemo" in self.tags

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProposedAction:
    kind: ActionKind
    urn: str
    value: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Finding:
    id: str
    asset: AssetSnapshot
    score: int
    severity: Severity
    title: str
    evidence: tuple[str, ...]
    actions: tuple[ProposedAction, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset.to_dict(),
            "score": self.score,
            "severity": self.severity,
            "title": self.title,
            "evidence": list(self.evidence),
            "actions": [action.to_dict() for action in self.actions],
        }

@dataclass
class ScanReport:
    mode: str
    synthetic_data_only: bool
    assets: list[AssetSnapshot]
    findings: list[Finding]
    tool_evidence: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in self.findings:
            counts[finding.severity] += 1
        return {
            "mode": self.mode,
            "synthetic_data_only": self.synthetic_data_only,
            "summary": {
                "assets_scanned": len(self.assets),
                "findings": len(self.findings),
                "severity": counts,
                "downstream_edges": sum(len(asset.downstream) for asset in self.assets),
            },
            "findings": [finding.to_dict() for finding in self.findings],
            "tool_evidence": self.tool_evidence,
        }
