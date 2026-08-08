# Devpost submission draft

## Project name

GraphMedic — Evidence-first catalog repair agent

## Tagline

See the metadata break, measure its blast radius, and repair it with proof.

## Inspiration

Catalog cleanup is often treated as a list of empty fields. In practice, the important question is graph-shaped: which incomplete or retired asset still feeds downstream decisions, and what is the smallest truthful repair a steward can make? GraphMedic turns that question into an explainable queue.

## What it does

GraphMedic searches an explicitly opted-in synthetic DataHub namespace, verifies entity metadata, traces lineage in both directions, and ranks stewardship risk using missing ownership, missing descriptions, downstream blast radius, and deprecated dependencies. It proposes bounded metadata repairs, shows the exact write to a human, performs only the approved mutation, and reads the entity back to verify success.

## How it was built

The backend is Python and FastAPI. A typed adapter launches the official DataHub MCP server over stdio and calls `search`, `get_entities`, `get_lineage`, `add_tags`, and `update_description`. DataHub OSS stores six fictional datasets and five fictional lineage edges seeded through the DataHub Python SDK. The UI is framework-free HTML, CSS, and JavaScript so the evidence trail stays fast and legible.

The browser never supplies a URN or write value. It submits only a finding ID, an action kind, and explicit approval. The server looks up the current reviewed proposal, verifies the three-marker synthetic boundary, runs the mutation, and verifies it with a fresh read.

## Challenges

The most important challenge was making writeback useful without making it dangerous. Search alone is not a sufficient safety boundary, so GraphMedic independently requires a demo namespace, the `GraphMedicDemo` tag, and a `SYNTHETIC` classification. It also refuses to invent owners or business meaning. A separate scanner checks public artifacts for private paths, addresses, credentials, emails, and network identifiers.

## Accomplishments

- Real bidirectional lineage analysis through the official MCP server.
- Approval-gated tag and description writeback with post-write verification.
- An explainable 115-point critical finding caused by combined owner, documentation, downstream, and deprecated-upstream evidence.
- Ten automated tests plus generic and user-specific privacy scans.
- A polished responsive UI, interactive sanitized reviewer preview, 120-second narrated demo, Apache-2.0 source, and reusable Agent Skill.

## What we learned

Metadata agents are most trustworthy when their authority is narrower than their insight. GraphMedic can search and reason broadly inside a clearly marked demo boundary, but its write vocabulary remains tiny, deterministic, reviewable, and verified.

## What's next

The same design can support organization-defined opt-in domains, richer stewardship queues, issue creation, policy-as-code scoring, and reversible patch sets. The deny-by-default adapter and Agent Skill are designed to be reusable building blocks.

## Built with

DataHub OSS, DataHub MCP Server, DataHub Python SDK, Python, FastAPI, Pydantic, HTML, CSS, JavaScript, pytest, Docker, and Remotion.

## Links to fill at handoff

- Public repository: `https://github.com/bgrubbs1/datahub-graphmedic`
- Interactive reviewer preview: `https://bgrubbs1.github.io/datahub-graphmedic/demo/`
- Public demo video: `https://youtu.be/Ds0y8EPFxxs`
