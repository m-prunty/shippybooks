# Diagrams

Class, project, and control flow diagrams for **shippybooks**, generated in
both **PNG** and **Mermaid (MMD)** forms.

## Files

| Diagram | PNG | Mermaid | Source |
|---------|-----|---------|--------|
| Class diagram | `classes.png` | `classes.mmd` | `pyreverse` (pylint) |
| Project / module diagram | `project.png` | `project.mmd` | `pyreverse` (pylint) |
| Control flow diagram | `control-flow.png` | `control-flow.mmd` | `control-flow.dot` (graphviz DOT) |

## Regenerating

```bash
make diagrams
```

This requires:

- **Python dependencies** (dev group in `pyproject.toml`):
  - `pylint` — provides the `pyreverse` command used for the class and
    project diagrams
  - `graphviz` — Python bindings; `make diagrams` also shells out to the
    `dot` binary
- **System package**: `graphviz` (provides `/usr/bin/dot`).
  - Debian/Ubuntu: `sudo apt-get install graphviz`

`pyreverse` analyses `src/shippybooks` and writes `classes.png` (class
hierarchy + associations) and `project.png` (package/module dependencies).
`control-flow.png` is rendered from `control-flow.dot` with `dot -Tpng`.

The `.mmd` files are Mermaid sources mirroring the same diagrams. Render
them with any Mermaid-compatible viewer (GitHub, Notion, Obsidian,
Mermaid Live Editor, etc.).

## Dependency graph

- `pylint` (`pyreverse`) → Python source → `classes.png` / `project.png`
- `graphviz` (`dot`) → `control-flow.dot` → `control-flow.png`
- Hand-authored Mermaid → `classes.mmd` / `project.mmd` / `control-flow.mmd`
