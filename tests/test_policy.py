from graphmedic.models import AssetSnapshot
from graphmedic.policy import analyze_assets


def demo_asset(**overrides):
    values = {
        "urn": "urn:li:dataset:(urn:li:dataPlatform:postgres,graphmedic_demo.curated.orders,PROD)",
        "name": "curated.orders",
        "platform": "postgres",
        "tags": ("GraphMedicDemo",),
    }
    values.update(overrides)
    return AssetSnapshot(**values)


def test_high_risk_owner_and_description_gap_is_ranked_with_blast_radius():
    asset = demo_asset(downstream=("revenue", "forecast", "dashboard"))
    finding = analyze_assets([asset])[0]

    assert finding.severity == "high"
    assert finding.score == 65
    assert [action.kind for action in finding.actions] == ["add_tag", "append_description"]
    assert "3 downstream asset(s)" in " ".join(finding.evidence)


def test_deprecated_dependency_escalates_to_critical():
    asset = demo_asset(
        owners=("urn:li:corpuser:synthetic-steward",),
        description="Synthetic curated orders.",
        downstream=("revenue", "forecast"),
        has_deprecated_upstream=True,
    )

    finding = analyze_assets([asset])[0]
    assert finding.severity == "critical"
    assert finding.score == 70


def test_private_or_unopted_assets_are_never_analyzed():
    private_asset = AssetSnapshot(
        urn="urn:li:dataset:(urn:li:dataPlatform:postgres,production.private.orders,PROD)",
        name="orders",
        platform="postgres",
    )
    namespace_only = demo_asset(tags=())

    assert analyze_assets([private_asset, namespace_only]) == []


def test_healthy_demo_asset_has_no_finding():
    asset = demo_asset(
        description="Synthetic orders with a documented owner.",
        owners=("urn:li:corpuser:synthetic-steward",),
        downstream=(),
    )
    assert analyze_assets([asset]) == []
