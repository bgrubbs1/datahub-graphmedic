from __future__ import annotations

from pathlib import Path

from graphmedic.privacy import scan_public_tree


def main() -> None:
    root = Path(__file__).parents[1]
    findings = scan_public_tree(root)
    if findings:
        print("Privacy scan failed:")
        for finding in findings:
            print(f"- {finding}")
        raise SystemExit(1)
    print("Privacy scan passed: no generic private-data patterns found.")


if __name__ == "__main__":
    main()
