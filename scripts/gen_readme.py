#!/usr/bin/env python3
"""Regenerate README.md diagram sections from diagrams/*.mmd sources.

Single source of truth: the .mmd files in diagrams/. This script rewrites the
Mermaid code blocks in README.md so they always match the .mmd sources, and
fails if a section header is missing (keeps CI honest).

Usage:
    python scripts/gen_readme.py
"""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DIAGRAMS = ROOT / "diagrams"

# (file stem, section header, description). Order matches README layout.
DIAGRAMS_ORDER = [
    (
        "classes",
        "### Class diagram",
        "The class diagram shows the domain model, commands, queries, events, "
        "repositories, handlers, notification layer, and application wiring. "
        "Generated from `src/shippybooks` with `pyreverse` (Pylint)",
    ),
    (
        "project",
        "### Project diagram",
        "The project diagram shows the `shippybooks` package structure, "
        "external dependencies, and runtime request flow between modules",
    ),
    (
        "control-flow",
        "### Control flow diagram",
        "The control flow diagram shows the write path (commands), query path "
        "(reads), health probe path, event-driven notifications, and optional "
        "persistence",
    ),
]


def section_block(name: str, header: str, description: str) -> str:
    mmd = (DIAGRAMS / f"{name}.mmd").read_text().strip()
    return (
        f"{header}\n\n"
        f"{description}. Source at `diagrams/{name}.mmd`.\n\n"
        f"```mermaid\n{mmd}\n```\n\n"
        f"View the rendered image: [diagrams/{name}.png](diagrams/{name}.png)\n"
    )


def regenerate(readme_text: str) -> str:
    for name, header, description in DIAGRAMS_ORDER:
        block = section_block(name, header, description)
        # Match from the header up to (but excluding) the next section header
        # ("### " or "## "), or end of file.
        pattern = re.compile(
            rf"{re.escape(header)}\n.*?(?=\n### |\n## |\Z)",
            re.DOTALL,
        )
        readme_text, count = pattern.subn(block.rstrip() + "\n", readme_text, count=1)
        if count == 0:
            raise SystemExit(f"error: section header '{header}' not found in README.md")
    return readme_text


def main() -> None:
    text = README.read_text()
    new_text = regenerate(text)
    if new_text != text:
        README.write_text(new_text)
        print("README.md regenerated from diagrams/*.mmd")
    else:
        print("README.md is already up to date")


if __name__ == "__main__":
    main()
