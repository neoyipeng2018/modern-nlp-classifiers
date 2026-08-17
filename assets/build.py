#!/usr/bin/env python3
"""Build the planning documents into self-contained HTML files at the repo root.

Each source fragment in assets/src/*.body.html holds only the page content.
This script wraps it in the shared shell and inlines assets/docs.css so the
generated file can be opened, mailed or dropped anywhere on its own.

    python assets/build.py
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "src"
CSS = ROOT / "assets" / "docs.css"

DOCS = [
    ("product", "PRODUCT.html", "Product spec"),
    ("program_design", "PROGRAM_DESIGN.html", "Program design"),
    ("architecture", "ARCHITECTURE.html", "Architecture"),
    ("vertical_slices", "VERTICAL_SLICES.html", "Vertical slices"),
]

SHELL = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description}">
  <title>{title}</title>
  <style>
{css}
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
{body}
  <a class="back-top" href="#top" aria-label="Back to top">&uarr;</a>
</body>
</html>
"""


def read_meta(text: str) -> tuple[str, str, str]:
    """Pull the <!--meta title / description --> header off a fragment."""
    title, description = "", ""
    lines = text.splitlines()
    body_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("<!--@title "):
            title = stripped[len("<!--@title ") : -len("-->")].strip()
        elif stripped.startswith("<!--@description "):
            description = stripped[len("<!--@description ") : -len("-->")].strip()
        else:
            body_start = i
            break
    if not title or not description:
        raise SystemExit("fragment is missing @title or @description")
    return title, description, "\n".join(lines[body_start:])


def main() -> int:
    css = CSS.read_text(encoding="utf-8").rstrip()
    for stem, out_name, _label in DOCS:
        src = SRC / f"{stem}.body.html"
        if not src.exists():
            print(f"skip {out_name}: {src.relative_to(ROOT)} not found")
            continue
        title, description, body = read_meta(src.read_text(encoding="utf-8"))
        html = SHELL.format(title=title, description=description, css=css, body=body.rstrip())
        (ROOT / out_name).write_text(html, encoding="utf-8")
        print(f"wrote {out_name} ({len(html) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
