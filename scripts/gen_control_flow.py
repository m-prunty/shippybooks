#!/usr/bin/env python3
"""Generate control-flow diagram (Mermaid) from source via AST.

Walks src/shippybooks and extracts:
  * FastAPI route decorators  -> endpoints, HTTP methods, paths
  * Function call edges       -> route handler -> service -> repo -> bus
  * Import/module deps        -> package grouping
  * bootstrap.build_app_state -> object graph wiring
  * main.create_app           -> router registration

Semantic relationships AST cannot resolve (isinstance command dispatch,
EventBus publish/subscribe matching, SSE streaming) are emitted as
dashed edges flagged with [inferred].

Usage:
    uv run python scripts/gen_control_flow.py
"""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "shippybooks"
OUT = ROOT / "diagrams" / "control-flow.mmd"

# Map filename -> module label used in the diagram
MODULE_LABELS = {
    "api/endpoints/books.py": "api/endpoints/books.py",
    "api/endpoints/orders.py": "api/endpoints/orders.py",
    "api/endpoints/notifications.py": "api/endpoints/notifications.py",
    "api/endpoints/health.py": "api/endpoints/health.py",
    "api/dependencies.py": "api/dependencies.py",
    "services/command_handlers.py": "services/command_handlers.py",
    "services/query_handlers.py": "services/query_handlers.py",
    "services/repos.py": "services/repos.py",
    "events/bus.py": "events/bus.py",
    "events/notifications.py": "events/notifications.py",
    "events/store.py": "events/store.py",
    "bootstrap.py": "bootstrap.py",
    "main.py": "main.py",
    "domain/models.py": "domain/models.py",
    "domain/commands.py": "domain/commands.py",
    "domain/queries.py": "domain/queries.py",
    "domain/events.py": "domain/events.py",
    "db/models.py": "db/models.py",
    "db/session.py": "db/session.py",
    "settings.py": "settings.py",
}


class SourceIndex:
    """Parsed view of every module under src/shippybooks."""

    def __init__(self) -> None:
        self.routes: list[dict] = []
        self.calls: dict[str, list[str]] = defaultdict(list)
        self.func_module: dict[str, str] = {}
        self.methods: dict[str, list[str]] = defaultdict(list)
        self.class_module: dict[str, str] = {}
        self.imports: dict[str, set[str]] = defaultdict(set)

    def add_route(self, method: str, path: str, func: str, module: str) -> None:
        self.routes.append(
            {"method": method, "path": path, "func": func, "module": module}
        )

    def add_call(self, caller: str, callee: str) -> None:
        if callee not in self.calls[caller]:
            self.calls[caller].append(callee)

    def set_func_module(self, func: str, module: str) -> None:
        self.func_module[func] = module

    def add_method(self, cls: str, method: str) -> None:
        if method not in self.methods[cls]:
            self.methods[cls].append(method)

    def set_class_module(self, cls: str, module: str) -> None:
        self.class_module[cls] = module

    def add_import(self, module: str, imported: str) -> None:
        self.imports[module].add(imported)


def decorator_method(dec: ast.expr) -> str | None:
    if isinstance(dec, ast.Attribute) and isinstance(dec.value, ast.Name):
        return dec.attr.upper()
    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
        return dec.func.attr.upper()
    return None


def decorator_path(dec: ast.expr) -> str | None:
    if isinstance(dec, ast.Call):
        for arg in dec.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                return arg.value
    return None


def _call_name(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


class SourceVisitor(ast.NodeVisitor):
    """Walks a single module, recording routes, calls, imports, classes."""

    def __init__(self, index: SourceIndex, module: str) -> None:
        self.index = index
        self.module = module
        self.in_class = False
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_in_class = self.in_class
        old_current = self.current_class
        self.in_class = True
        self.current_class = node.name
        self.index.set_class_module(node.name, self.module)
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                full = f"{node.name}.{item.name}"
                self.index.set_func_module(full, self.module)
                self.index.add_method(node.name, item.name)
                self._collect_calls(item, full)
        self.in_class = old_in_class
        self.current_class = old_current
        # Do NOT generic_visit: we already handled the class body.

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.in_class:
            return  # handled in visit_ClassDef
        full = node.name
        self.index.set_func_module(full, self.module)
        for dec in node.decorator_list:
            method = decorator_method(dec)
            path_str = decorator_path(dec)
            if method and path_str:
                self.index.add_route(method, path_str, full, self.module)
        self._collect_calls(node, full)
        self.generic_visit(node)  # descend into nested functions

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.index.add_import(self.module, alias.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.index.add_import(self.module, node.module.split(".")[0])
        self.generic_visit(node)

    def _collect_calls(self, node: ast.AST, caller: str) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                callee = _call_name(child)
                if callee:
                    self.index.add_call(caller, callee)


def analyze(index: SourceIndex) -> None:
    for path in sorted(SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(), filename=str(path))
        except SyntaxError:
            continue
        rel = path.relative_to(SRC)
        module = MODULE_LABELS.get(str(rel), str(rel))
        visitor = SourceVisitor(index, module)
        visitor.visit(tree)


def node_id(text: str) -> str:
    safe = "".join(c if c.isalnum() or c == "_" else "_" for c in text)
    return safe


def escape_mmd_label(label: str) -> str:
    """Escape Mermaid special characters in edge/node labels.

    Curly braces are interpreted as diamond-shape syntax, parentheses as
    subroutine syntax, and square brackets as circle/stadium syntax in
    edge labels, so they must be HTML-entity-escaped.
    """
    return (
        label.replace("{", "&#123;")
        .replace("}", "&#125;")
        .replace("(", "&#40;")
        .replace(")", "&#41;")
        .replace("[", "&#91;")
        .replace("]", "&#93;")
    )


def edge(src: str, label: str, dst: str, style: str = "-->") -> str:
    """Build an edge line with the label Mermaid-escaped."""
    safe_label = escape_mmd_label(label)
    return f"    {src} {style}|{safe_label}| {dst}"


def emit(index: SourceIndex) -> str:
    lines: list[str] = []
    lines.append("flowchart TD")
    lines.append("    %% Auto-generated control flow diagram")
    lines.append("    %% Source: scripts/gen_control_flow.py")
    lines.append("    %% Edges marked [inferred] are not directly observable from AST")
    lines.append("")

    # ---- styling ----
    lines.append("    classDef default fill:#e8f0fe,stroke:#1d4ed8,stroke-width:1px")
    lines.append("    classDef endpoint fill:#f0f9ff,stroke:#0284c7,stroke-width:1px")
    lines.append("    classDef handler fill:#fef2f2,stroke:#ef4444,stroke-width:1px")
    lines.append("    classDef query fill:#f0f9ff,stroke:#0284c7,stroke-width:1px")
    lines.append("    classDef repo fill:#f0fdf4,stroke:#16a34a,stroke-width:1px")
    lines.append("    classDef bus fill:#fffbeb,stroke:#d97706,stroke-width:1px")
    lines.append("    classDef db fill:#e0f2fe,stroke:#0369a1,stroke-width:1px")
    lines.append("")

    # ---- HTTP client ----
    lines.append('    Client(("HTTP client"))')
    lines.append("")

    # ---- API subgraph ----
    lines.append("    subgraph API [\"FastAPI HTTP layer\"]")
    for r in index.routes:
        nid = node_id(r["func"])
        label = f'{r["method"]} {r["path"]}\\n{r["func"]}'
        lines.append(f'        {nid}["{label}"]:::endpoint')
    lines.append("    end")
    lines.append("")

    # ---- Deps ----
    lines.append("    Deps[\"api/dependencies.py\\nDepends wiring\"]")
    lines.append("")

    # ---- Bootstrap / main ----
    lines.append("    Main[\"main.py\\ncreate_app()\"]")
    lines.append("    Bootstrap[\"bootstrap.py\\nbuild_app_state()\"]")
    lines.append("")

    # ---- Command side ----
    lines.append("    subgraph Command [\"Command side (writes)\"]")
    for m in index.methods.get("CommandHandler", []):
        nid = node_id(f"CommandHandler.{m}")
        lines.append(f'        {nid}["CommandHandler.{m}"]:::handler')
    lines.append("    end")
    lines.append("")

    # ---- Query side ----
    lines.append("    subgraph Query [\"Query side (reads)\"]")
    for m in index.methods.get("QueryHandler", []):
        nid = node_id(f"QueryHandler.{m}")
        lines.append(f'        {nid}["QueryHandler.{m}"]:::query')
    lines.append("    end")
    lines.append("")

    # ---- Repos ----
    lines.append("    Repos[\"services/repos.py\\nBookRepository · OrderRepository\"]:::repo")
    lines.append("")

    # ---- Bus / events ----
    lines.append("    subgraph Events [\"Event-driven notifications\"]")
    lines.append('        style Events fill:#fffbeb,stroke:#d97706,stroke-width:1px')
    for m in index.methods.get("EventBus", []):
        nid = node_id(f"EventBus.{m}")
        lines.append(f'        {nid}["EventBus.{m}"]:::bus')
    for m in index.methods.get("NotificationDispatcher", []):
        nid = node_id(f"NotificationDispatcher.{m}")
        lines.append(f'        {nid}["NotificationDispatcher.{m}"]:::bus')
    lines.append("    end")
    lines.append("")

    # ---- Notification handler ----
    lines.append("    NH[\"NotificationHandler.dispatch()\"]:::bus")
    lines.append("")

    # ---- Persistence ----
    lines.append("    subgraph Persist [\"Persistence\"]")
    lines.append('        ORM["db/models.py\\nSQLAlchemy ORM models"]:::db')
    lines.append('        Session["db/session.py\\nengine · get_session()\\nSQLite (data.db)"]:::db')
    lines.append("    end")
    lines.append("")

    # ---- Store ----
    lines.append('    Store[("events/store.py\\nNotificationStore")]')
    lines.append("")

    # ---- Domain model nodes ----
    lines.append("    DM[\"domain/models.py\\nBook · Order · OrderItem\"]")
    lines.append("    DC[\"domain/commands.py\\nCommand hierarchy\"]")
    lines.append("    DQ[\"domain/queries.py\\nQuery hierarchy\"]")
    lines.append("")

    # ---- Edges: client -> endpoints ----
    lines.append("    %% Runtime request flow")
    for r in index.routes:
        nid = node_id(r["func"])
        lines.append(edge("Client", f'{r["method"]} {r["path"]}', nid))

    lines.append("")
    lines.append("    %% Endpoint -> dependency wiring")

    # Endpoint -> Deps (heuristic: endpoint functions that call into deps module)
    for r in index.routes:
        nid = node_id(r["func"])
        func = r["func"]
        for callee in index.calls.get(func, []):
            callee_mod = index.func_module.get(callee, "")
            if "dependencies" in callee_mod:
                lines.append(f"    {nid} --> Deps")
                break

    # Deps -> handlers
    lines.append(edge("Deps", "CmdHandlerDep", "CommandHandler.handle"))
    lines.append(edge("Deps", "QueryHandlerDep", "QueryHandler.handle"))

    # Bootstrap wiring
    lines.append(edge("Main", "build_app_state()", "Bootstrap"))
    lines.append("    Bootstrap -.->|wire| CommandHandler.handle")
    lines.append("    Bootstrap -.->|wire| QueryHandler.handle")
    lines.append("    Bootstrap -.->|wire| Store")

    # ---- Command handler flow ----
    lines.append("")
    lines.append("    %% Command side")
    lines.append(edge("CommandHandler.handle", "isinstance dispatch [inferred]", "DC"))
    lines.append("    CommandHandler.handle -->|mutate| DM")
    lines.append("    CommandHandler.handle -->|save / get| Repos")

    # ---- Query handler flow ----
    lines.append("")
    lines.append("    %% Query side")
    lines.append("    QueryHandler.handle -->|get / all| Repos")
    lines.append(edge("QueryHandler.handle", "to_domain()", "DM"))

    # ---- Repos -> ORM ----
    lines.append("")
    lines.append("    %% Persistence")
    lines.append("    Repos -->|SQLAlchemy Session| ORM")
    lines.append("    ORM -->|bind| Session")

    # ---- Event bus flow ----
    lines.append("")
    lines.append("    %% Event-driven notifications")
    lines.append(edge("CommandHandler.handle", "publish(event) [inferred]", "EventBus.publish"))
    lines.append(edge("EventBus.publish", "subscribe match [inferred]", "NotificationDispatcher.on_*"))
    lines.append("    NotificationDispatcher.on_* -->|build Notification| NH")
    lines.append(edge("NH", "append()", "Store"))

    # ---- SSE stream back to client ----
    lines.append("")
    lines.append("    %% SSE stream back to client")
    lines.append(
        edge(
            "Store",
            "SSE stream: GET /api/v1/notifications/stream [inferred]",
            "Client",
            style="-.->",
        )
    )

    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    index = SourceIndex()
    analyze(index)
    mmd = emit(index)
    OUT.write_text(mmd)
    print(
        f"Wrote {OUT} "
        f"({len(index.routes)} routes, {len(index.calls)} call sites, "
        f"{len(index.func_module)} functions)"
    )


if __name__ == "__main__":
    main()
