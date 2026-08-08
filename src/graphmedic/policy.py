from __future__ import annotations

import hashlib

from .models import AssetSnapshot, Finding, ProposedAction, Severity


REVIEW_TAG = "GraphMedicReviewed"


def _severity(score: int) -> Severity:
    if score >= 70:
        return "critical"
    if score >= 45:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def _finding_id(asset: AssetSnapshot, evidence: list[str]) -> str:
    material = "|".join((asset.urn, *sorted(evidence)))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def analyze_assets(assets: list[AssetSnapshot]) -> list[Finding]:
    """Return deterministic, reviewable findings for explicitly synthetic assets.

    The allowlist is a privacy and write-safety boundary: GraphMedic will neither
    analyze nor mutate an asset unless both its URN namespace and demo tag opt in.
    """

    findings: list[Finding] = []
    for asset in assets:
        if not asset.is_demo_asset:
            continue

        evidence: list[str] = []
        score = 0
        if not asset.owners:
            score += 30
            evidence.append("No owner is recorded in DataHub")
        if not asset.description.strip():
            score += 20
            evidence.append("No human-readable description is recorded")
        if asset.downstream:
            blast_score = min(20, len(asset.downstream) * 5)
            score += blast_score
            evidence.append(f"{len(asset.downstream)} downstream asset(s) are in the blast radius")
        if asset.has_deprecated_upstream:
            # A live consumer fed by a deprecated source is an immediate
            # operational risk, not merely a documentation-quality issue.
            score += 60
            evidence.append("A deprecated upstream asset still feeds this dataset")
        if not evidence:
            continue

        severity = _severity(score)
        actions: list[ProposedAction] = []
        if REVIEW_TAG not in asset.tags:
            actions.append(
                ProposedAction(
                    kind="add_tag",
                    urn=asset.urn,
                    value=REVIEW_TAG,
                    reason="Mark the asset as reviewed without inventing an owner",
                )
            )
        if not asset.description.strip():
            actions.append(
                ProposedAction(
                    kind="append_description",
                    urn=asset.urn,
                    value=(
                        "GraphMedic review: metadata stewardship is required. "
                        f"Current synthetic lineage shows {len(asset.downstream)} downstream asset(s)."
                    ),
                    reason="Add evidence-based context while leaving business facts for a human steward",
                )
            )

        title_bits = []
        if not asset.owners:
            title_bits.append("owner gap")
        if not asset.description.strip():
            title_bits.append("documentation gap")
        if asset.has_deprecated_upstream:
            title_bits.append("deprecated dependency")
        if not title_bits:
            title_bits.append("lineage exposure")

        findings.append(
            Finding(
                id=_finding_id(asset, evidence),
                asset=asset,
                score=score,
                severity=severity,
                title=" + ".join(title_bits).title(),
                evidence=tuple(evidence),
                actions=tuple(actions),
            )
        )

    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(findings, key=lambda item: (order[item.severity], -item.score, item.asset.name))
