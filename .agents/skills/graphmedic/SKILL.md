---
name: graphmedic
description: Triage and repair an explicitly synthetic DataHub demo catalog through the official MCP server.
---

# GraphMedic skill

Use this skill only for assets that independently satisfy every marker below:

1. The URN contains `graphmedic_demo`.
2. The entity has the `GraphMedicDemo` tag.
3. The `data_classification` custom property equals `SYNTHETIC`.

Start read-only. Use `search`, `get_entities`, and both upstream and downstream `get_lineage` calls to collect evidence. Rank missing ownership, missing descriptions, downstream blast radius, and deprecated dependencies. Explain each proposed repair using observed metadata only.

Never infer or invent owners, business meaning, or sensitivity. Never access another namespace. Require explicit human approval before any mutation. The only permitted writes are adding `urn:li:tag:GraphMedicReviewed` and appending a note that begins `GraphMedic review:`. After a write, call `get_entities` again and report whether verification succeeded.
