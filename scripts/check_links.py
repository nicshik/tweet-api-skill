#!/usr/bin/env python3
"""Check repository-local Markdown links."""

from __future__ import annotations

import re
import sys
import urllib.parse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INLINE_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
REFERENCE_LINK_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def markdown_files() -> list[Path]:
    candidates = [
        *ROOT.glob("*.md"),
        *ROOT.glob("references/*.md"),
        *ROOT.glob(".github/*.md"),
        *ROOT.glob(".github/ISSUE_TEMPLATE/*.md"),
    ]
    return sorted(path for path in candidates if path.is_file())


def strip_code_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def normalize_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<"):
        target = target[1:].split(">", 1)[0].strip()
    else:
        target = target.split(maxsplit=1)[0].strip()

    if not target or target.startswith("#"):
        return None
    if target.startswith("//") or SCHEME_RE.match(target):
        return None

    parsed = urllib.parse.urlsplit(target)
    path = urllib.parse.unquote(parsed.path)
    return path or None


def missing_links(path: Path) -> list[str]:
    text = strip_code_fences(path.read_text(encoding="utf-8"))
    raw_targets = [
        *(match.group(1) for match in INLINE_LINK_RE.finditer(text)),
        *(match.group(1) for match in REFERENCE_LINK_RE.finditer(text)),
    ]

    missing: list[str] = []
    for raw_target in raw_targets:
        target = normalize_target(raw_target)
        if target is None:
            continue

        if target.startswith("/"):
            target_path = ROOT / target.lstrip("/")
        else:
            target_path = path.parent / target
        if not target_path.exists():
            missing.append(raw_target)

    return missing


def main() -> int:
    failures: list[str] = []
    for path in markdown_files():
        for target in missing_links(path):
            failures.append(f"{path.relative_to(ROOT)}: missing link target {target}")

    if failures:
        sys.stderr.write("Broken local Markdown links found:\n")
        for failure in failures:
            sys.stderr.write(f"- {failure}\n")
        return 1

    print("Local Markdown links OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
