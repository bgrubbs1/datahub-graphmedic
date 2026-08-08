# Architecture

```text
Browser UI
  │  finding ID + action kind + explicit approval only
  ▼
FastAPI service ── current server-side proposal cache ── JSONL audit
  │
  ▼
Three-marker policy gate
  │  namespace + tag + SYNTHETIC property
  ▼
Official DataHub MCP server
  │  search / get_entities / get_lineage / add_tags / update_description
  ▼
DataHub OSS Core ── six fictional datasets + five fictional lineage edges
```

Risk scoring is deterministic and explainable: missing owner adds 30, missing description adds 20, each downstream asset adds 5 up to 20, and a deprecated upstream adds 60. The queue sorts by severity, score, and name.

The client cannot submit arbitrary mutation material. Proposed actions live in server memory and are looked up from a fresh scan. The adapter validates the namespace, tag, classification, operation, and value before launching a mutation tool. A post-write entity read proves that the asset remains inside the boundary.
