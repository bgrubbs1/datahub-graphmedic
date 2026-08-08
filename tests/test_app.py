from pathlib import Path

from fastapi.testclient import TestClient

from graphmedic.app import create_app


def test_health_declares_privacy_boundary(tmp_path: Path) -> None:
    client = TestClient(create_app("fixture", tmp_path / "audit.jsonl"))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["synthetic_data_only"] is True


def test_scan_and_approval_gate(tmp_path: Path) -> None:
    client = TestClient(create_app("fixture", tmp_path / "audit.jsonl"))
    scanned = client.post("/api/scan")
    assert scanned.status_code == 200
    finding = scanned.json()["findings"][0]

    rejected = client.post(
        "/api/apply",
        json={"finding_id": finding["id"], "action_kind": "add_tag", "approved": False},
    )
    assert rejected.status_code == 403

    accepted = client.post(
        "/api/apply",
        json={"finding_id": finding["id"], "action_kind": "add_tag", "approved": True},
    )
    assert accepted.status_code == 200
    assert accepted.json()["event"]["synthetic_data_only"] is True
    assert len(client.get("/api/audit").json()) == 1
