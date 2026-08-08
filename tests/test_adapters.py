import pytest

from graphmedic.adapters import DataHubMCPAdapter, _is_allowlisted
from graphmedic.models import ProposedAction


def entity(*, urn: str, tags: list[str], classification: str) -> dict[str, object]:
    return {
        "urn": urn,
        "properties": {
            "customProperties": [{"key": "data_classification", "value": classification}]
        },
        "tags": {
            "tags": [
                {"tag": {"urn": f"urn:li:tag:{tag}", "properties": {"name": tag}}}
                for tag in tags
            ]
        },
    }


def test_allowlist_requires_all_three_markers() -> None:
    urn = "urn:li:dataset:(urn:li:dataPlatform:graphmedic_demo,demo.orders,PROD)"
    assert _is_allowlisted(entity(urn=urn, tags=["GraphMedicDemo"], classification="SYNTHETIC"))
    assert not _is_allowlisted(entity(urn=urn, tags=[], classification="SYNTHETIC"))
    assert not _is_allowlisted(entity(urn=urn, tags=["GraphMedicDemo"], classification="PRIVATE"))
    assert not _is_allowlisted(
        entity(
            urn="urn:li:dataset:(urn:li:dataPlatform:company,orders,PROD)",
            tags=["GraphMedicDemo"],
            classification="SYNTHETIC",
        )
    )


@pytest.mark.asyncio
async def test_mutation_rejects_non_demo_urn_before_mcp_launch() -> None:
    adapter = DataHubMCPAdapter()
    with pytest.raises(PermissionError, match="outside the synthetic demo namespace"):
        await adapter.apply_action(
            ProposedAction(
                kind="add_tag",
                urn="urn:li:dataset:(urn:li:dataPlatform:company,orders,PROD)",
                value="GraphMedicReviewed",
                reason="test",
            )
        )
