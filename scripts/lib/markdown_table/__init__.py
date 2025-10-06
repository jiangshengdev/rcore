"""Markdown table utilities package.

This package provides a converter that expands <br> inside pipe-table cells
into multiple rows. Designed to be idempotent and conservative: it only
rewrites data rows that actually contain <br>, leaving other content intact.

Entrypoint module: scripts.lib.markdown_table.main
"""

__all__ = []
