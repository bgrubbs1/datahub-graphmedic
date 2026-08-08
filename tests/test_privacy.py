from pathlib import Path

from graphmedic.privacy import scan_public_tree


def test_public_tree_rejects_private_network_addresses(tmp_path: Path):
    private_address = ".".join(("192", "168", "4", "20"))
    (tmp_path / "leak.md").write_text(f"internal host: {private_address}", encoding="utf-8")
    assert scan_public_tree(tmp_path) == ["leak.md: RFC1918 IPv4 address"]


def test_public_tree_allows_documented_example_addresses(tmp_path: Path):
    (tmp_path / "safe.md").write_text("contact: steward@example.com", encoding="utf-8")
    assert scan_public_tree(tmp_path) == []
