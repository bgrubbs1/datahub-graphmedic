from __future__ import annotations

from datahub.emitter.mce_builder import make_dataset_urn, make_tag_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DataHubRestEmitter
from datahub.metadata.schema_classes import (
    DatasetLineageTypeClass,
    DatasetPropertiesClass,
    DeprecationClass,
    GlobalTagsClass,
    OwnershipClass,
    OwnershipTypeClass,
    OwnerClass,
    TagAssociationClass,
    TagPropertiesClass,
    UpstreamClass,
    UpstreamLineageClass,
)


GMS_URL = "http://127.0.0.1:18080"
PLATFORM = "graphmedic_demo"
DEMO_TAG = make_tag_urn("GraphMedicDemo")
REVIEW_TAG = make_tag_urn("GraphMedicReviewed")
ACTOR = "urn:li:corpuser:graphmedic-bot"
STEWARD = "urn:li:corpuser:synthetic-steward"


def dataset(name: str) -> str:
    return make_dataset_urn(PLATFORM, name, "PROD")


def emit(emitter: DataHubRestEmitter, urn: str, aspect: object) -> None:
    emitter.emit(MetadataChangeProposalWrapper(entityUrn=urn, aspect=aspect))


def main() -> None:
    emitter = DataHubRestEmitter(GMS_URL)
    emitter.test_connection()

    emit(
        emitter,
        DEMO_TAG,
        TagPropertiesClass(
            name="GraphMedicDemo",
            description="Explicit opt-in marker for GraphMedic's fictional demonstration assets.",
            colorHex="#28E07B",
        ),
    )
    emit(
        emitter,
        REVIEW_TAG,
        TagPropertiesClass(
            name="GraphMedicReviewed",
            description="Review marker written by GraphMedic after explicit human approval.",
            colorHex="#49B7FF",
        ),
    )

    assets = {
        "retired_v1": dataset("demo_ops.retired_orders_v1"),
        "orders": dataset("demo_ops.orders_clean"),
        "customers": dataset("demo_ops.customers_clean"),
        "revenue": dataset("demo_analytics.daily_revenue"),
        "dashboard": dataset("demo_analytics.executive_snapshot"),
        "stable": dataset("demo_reference.currency_rates"),
    }
    descriptions = {
        "retired_v1": "Fictional legacy order feed retained to demonstrate deprecated-lineage detection.",
        "orders": "",
        "customers": "Fictional, non-personal customer segments for the GraphMedic demo.",
        "revenue": "",
        "dashboard": "",
        "stable": "Fictional reference rates used only in the synthetic GraphMedic catalog.",
    }
    owned = {"customers", "stable"}

    for key, urn in assets.items():
        emit(
            emitter,
            urn,
            DatasetPropertiesClass(
                name=key.replace("_", " ").title(),
                description=descriptions[key],
                customProperties={
                    "data_classification": "SYNTHETIC",
                    "contest_demo": "true",
                },
            ),
        )
        emit(emitter, urn, GlobalTagsClass(tags=[TagAssociationClass(tag=DEMO_TAG)]))
        if key in owned:
            emit(
                emitter,
                urn,
                OwnershipClass(
                    owners=[OwnerClass(owner=STEWARD, type=OwnershipTypeClass.DATAOWNER)]
                ),
            )

    emit(
        emitter,
        assets["retired_v1"],
        DeprecationClass(
            deprecated=True,
            note="Fictional source retired after the demo schema migration.",
            actor=ACTOR,
            replacement=assets["orders"],
        ),
    )

    relationships = {
        "orders": ["retired_v1"],
        "revenue": ["orders", "customers"],
        "dashboard": ["revenue", "stable"],
    }
    for downstream, upstreams in relationships.items():
        emit(
            emitter,
            assets[downstream],
            UpstreamLineageClass(
                upstreams=[
                    UpstreamClass(
                        dataset=assets[upstream],
                        type=DatasetLineageTypeClass.TRANSFORMED,
                    )
                    for upstream in upstreams
                ]
            ),
        )

    print(f"Seeded {len(assets)} fictional datasets and {sum(map(len, relationships.values()))} lineage edges.")


if __name__ == "__main__":
    main()
