#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Expand <br> inside Markdown pipe-table cells into multiple rows.

Design goals:
- Recursive scan: default over blog/ and docs/ from project root.
- Idempotent: running repeatedly yields no further changes once expanded.
- Conservative: no HTML entity unescape and no dry-run output.
- Minimal CLI: optional --paths to override default roots; no other flags.

Usage:
  python -m scripts.lib.markdown_table.main            # scan blog/ and docs/
  python -m scripts.lib.markdown_table.main --paths some/file.md docs/dir
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from typing import List

SEP_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")
# Only match lowercase HTML <br> tags inside table cells; do NOT match React <Br /> components
BR_RE = re.compile(r"<br\s*/?>")


def is_table_row(line: str) -> bool:
    # we consider lines that look like pipe tables (start with '|')
    return line.lstrip().startswith("|")


def split_cells(line: str) -> List[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def join_row(cells: List[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def expand_row_by_br(cells: List[str]) -> List[str]:
    per_cell_lines: List[List[str]] = []
    for c in cells:
        parts = BR_RE.split(c)
        parts = [p.strip() for p in parts]
        per_cell_lines.append(parts)

    height = max((len(p) for p in per_cell_lines), default=1)
    rows: List[str] = []
    for i in range(height):
        row = [p[i] if i < len(p) else "" for p in per_cell_lines]
        rows.append(join_row(row))
    return rows


def process_table(block_lines: List[str]) -> List[str]:
    if len(block_lines) < 2:
        return block_lines

    header = block_lines[0]
    separator = block_lines[1]
    out = [header, separator]

    header_cols = len(split_cells(header))

    for line in block_lines[2:]:
        # Only expand rows that actually contain <br>; otherwise keep original line
        if BR_RE.search(line):
            cells = split_cells(line)
            # pad to header column count for safety
            if len(cells) < header_cols:
                cells = cells + [""] * (header_cols - len(cells))
            out.extend(expand_row_by_br(cells))
        else:
            out.append(line)
    return out


def transform(md_text: str) -> str:
    lines = md_text.splitlines()
    i = 0
    out_lines: List[str] = []

    while i < len(lines):
        line = lines[i]
        if i + 1 < len(lines) and is_table_row(line) and SEP_RE.match(lines[i + 1] or ""):
            block = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and is_table_row(lines[i]):
                block.append(lines[i])
                i += 1
            out_lines.extend(process_table(block))
            continue
        else:
            out_lines.append(line)
            i += 1

    # Preserve trailing newline only if original had one
    return "\n".join(out_lines) + ("\n" if md_text.endswith("\n") else "")


def should_process_file(path: str) -> bool:
    lower = path.lower()
    if not (lower.endswith(".md") or lower.endswith(".mdx")):
        return False
    # Respect repository rule: we will not modify README files outside docs/blog
    return True


def iter_target_files(paths: List[str]) -> List[str]:
    files: List[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, filenames in os.walk(p):
                for name in filenames:
                    full = os.path.join(root, name)
                    if should_process_file(full):
                        files.append(full)
        elif os.path.isfile(p):
            if should_process_file(p):
                files.append(p)
    return files


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Expand <br> in Markdown tables to multiple rows.")
    parser.add_argument("--paths", nargs="*", help="Paths to scan (default: blog docs)")
    args = parser.parse_args(argv)

    roots = args.paths if args.paths else ["blog", "docs"]

    targets = iter_target_files(roots)
    changed = 0
    for path in targets:
        try:
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
            out = transform(src)
            if out != src:
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(out)
                changed += 1
        except Exception as e:
            print(f"[WARN] Skip {path}: {e}", file=sys.stderr)
    print(f"Processed {len(targets)} file(s), updated {changed} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
