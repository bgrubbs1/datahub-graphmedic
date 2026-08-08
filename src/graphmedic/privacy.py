from __future__ import annotations

import re
import os
from pathlib import Path


TEXT_SUFFIXES = {".css", ".html", ".json", ".md", ".py", ".toml", ".txt", ".yml", ".yaml"}
IGNORED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".cache",
    ".remotion",
    "node_modules",
    "out",
    "runtime",
}
GENERIC_PRIVATE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("absolute Windows path", re.compile(r"(?i)\b[A-Z]:\\(?:Users|Bee|Work|Documents)\\")),
    ("RFC1918 IPv4 address", re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b")),
    ("non-example email address", re.compile(r"(?i)\b[A-Z0-9._%+-]+@(?!example\.(?:com|org)\b)[A-Z0-9.-]+\.[A-Z]{2,}\b")),
    ("credential-like assignment", re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*['\"][^'\"]{8,}")),
)


def scan_public_tree(root: Path) -> list[str]:
    findings: list[str] = []
    for directory, names, files in os.walk(root):
        names[:] = sorted(
            name for name in names if name not in IGNORED_PARTS and not name.endswith(".egg-info")
        )
        for name in sorted(files):
            path = Path(directory) / name
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for label, pattern in GENERIC_PRIVATE_PATTERNS:
                if pattern.search(text):
                    findings.append(f"{path.relative_to(root)}: {label}")
    return findings
