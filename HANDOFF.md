# shippybooks handoff

_Last updated: 2026-11-19_

## Snapshot

- **Repository:** `shippybooks`
- **Branch:** `oc/health-api`
- **Base:** `origin/master` at `9d9274a`
- **Purpose:** CQRS-style FastAPI bookstore with in-process events, SSE notifications, optional SQLAlchemy persistence, and operational health endpoints.
- **Push state:** The branch commits are local and have not been pushed to `origin`.

## Work completed

### Health API

- Added `/health/live`, `/health/ready`, and `/health` endpoints.
- Added database, configuration, handler, and notification readiness checks.
- Required-check failures return HTTP 503; optional notification failures degrade the result without failing readiness.
- Added typed response models and health tests.
- Corrected probe timeout handling so a stuck dependency cannot hold the request beyond its deadline.

### Repository and API fixes

- Initialized `persistent_memory` for sessionless repositories, preventing an `AttributeError` in the default in-memory path.
- Made repository session parameters explicitly optional.
- Allowed local Vite origins through both `localhost` and `127.0.0.1` on arbitrary development ports.

### Documentation and tooling

- Added `ABOUT.md` with the implemented architecture, persistence behavior, and project motivations.
- Linked the overview from `README.md`.
- Added `.github/copilot-instructions.md` with build, test, lint, and architecture guidance.
- Added an OpenCode V2 project configuration for a local Ollama provider.
- Added development dependencies for Graphviz Python bindings and Pylint (which provides the `pyreverse` CLI).

### Diagrams

The `diagrams/` directory now contains class, project, and control-flow diagrams in both PNG and Mermaid form:

| Diagram | PNG | Mermaid | Generation source |
|---|---|---|---|
| Class | `diagrams/classes.png` | `diagrams/classes.mmd` | `pyreverse` for PNG; curated Mermaid source |
| Project / modules | `diagrams/project.png` | `diagrams/project.mmd` | `pyreverse` for PNG; curated Mermaid source |
| Control flow | `diagrams/control-flow.png` | `diagrams/control-flow.mmd` | Graphviz DOT for PNG; matching Mermaid source |

`diagrams/control-flow.dot` is the editable source for the control-flow PNG. See `diagrams/README.md` for regeneration instructions.

## Current architecture

### Request and command flow

1. FastAPI endpoints under `src/shippybooks/api/endpoints/` validate HTTP payloads.
2. Typed dependencies in `src/shippybooks/api/dependencies.py` retrieve shared handlers from `AppState`.
3. `CommandHandler` mutates aggregates through `BookRepository` and `OrderRepository`.
4. The handler publishes a domain event through the synchronous in-process `EventBus`.
5. `NotificationDispatcher` maps the event to a notification, and `NotificationHandler` appends it to `NotificationStore`.
6. `GET /api/v1/notifications/stream` exposes stored notifications as SSE and supports `last-event-id` resumption.

### Query flow

1. Query endpoints build immutable query models.
2. `QueryHandler` dispatches by query type.
3. Repositories return in-memory aggregates by default or ORM-backed values when persistent mode is enabled.
4. Endpoints serialize the result or return HTTP 404 for a missing book or order.

### Persistence state

- `settings.persistent_memory` defaults to `False`, so normal command/query tests use the in-memory repositories.
- SQLAlchemy models and a SQLite engine exist under `src/shippybooks/db/`.
- The startup hook creates the configured database schema.
- The persistence path is not yet production-ready; see the known issues below.

### Health state

- `/health/live` is a process-level liveness probe.
- `/health/ready` runs required database and configuration checks plus handler and notification checks.
- `/health` provides aggregate diagnostics and supports `verbose` and `deep` query options.
- Health routes are registered at the application root rather than under `/api/v1`, which is intentional for infrastructure probes.

## Validation status

### Passing

- `make test`: **16 passed**.
- `make diagrams`: class, project, and control-flow PNGs regenerate successfully.
- `uv run mypy --strict src/shippybooks/api/endpoints/health.py`: **no issues**.
- `git diff --check`: clean.

### Existing warnings and failures

- `make lint` still reports **16 strict MyPy errors** in pre-existing code, primarily in the database models/session, ORM repository updates, bootstrap session wiring, event typing, and service re-exports.
- Pytest reports deprecation warnings for FastAPI's `on_event("startup")` hook and Pydantic's class-based `Settings.Config`.
- The class and project PNGs are intentionally wide because they show the complete analyzed package; the Mermaid versions are usually easier to navigate.

## Known issues and risks

1. **ORM persistence path is incomplete.** `BookRepository.save()` references the undefined `book_orm` name when inserting a new persistent book.
2. **Order ORM updates are incomplete.** `OrderRepository.save()` calls `OrderORM.update_from_domain()`, but that method is not implemented.
3. **Orders are not wired persistently.** `bootstrap.py` creates `OrderRepository()` without the SQLAlchemy session used for books.
4. **ORM tests can exercise the fallback.** `tests/orm_test.py` does not enable `persistent_memory`, so it can pass while using in-memory dictionaries rather than the ORM.
5. **Strict typing is not clean.** The existing 16 MyPy errors should be resolved before treating `make lint` as a release gate.
6. **Startup lifecycle APIs are deprecated.** Replace FastAPI `on_event` with a lifespan handler and migrate Pydantic settings to `ConfigDict`.
7. **Events are process-local.** The event bus and notification store are in memory; there is no durable outbox, retry policy, or append-only domain-event store.
8. **Readiness assumes database availability.** The database is marked required even though in-memory persistence is the default; this is appropriate if startup/schema management remains SQLAlchemy-backed, but should be confirmed as the deployment contract.

## Useful commands

```bash
make install          # Install project and development dependencies
make test             # Run the pytest suite
make lint             # Run strict MyPy checks
make diagrams         # Regenerate PNG diagrams
make run              # Start the FastAPI app with reload enabled
```

Diagram generation also requires the Graphviz `dot` executable. On Debian/Ubuntu:

```bash
sudo apt-get install graphviz
```

## Recommended next steps

1. Fix and test the real SQLAlchemy persistence path, including a new order update conversion and session-aware repository tests.
2. Resolve the strict MyPy baseline and make `make lint` a required CI check.
3. Migrate startup configuration to FastAPI lifespan events and Pydantic `ConfigDict`.
4. Decide whether readiness should require SQLite in every deployment, then encode that rule in settings and tests.
5. Add CI for tests, typing, and deterministic diagram regeneration.
6. If durable delivery is required, design the outbox/event-store boundary before expanding the notification flow.

## Commit history on this branch

- `8cf6159 fix(repos): support sessionless in-memory repositories`
- `304196c feat(api): add liveness and readiness health endpoints`
- `12c36ac fix(cors): allow local origins on arbitrary ports`
- `170f4d1 docs: document project architecture and workflows`
- `8dde4e6 chore(opencode): configure local Ollama provider`
- `b62288b chore(git): ignore local runtime artifacts`
- `2f87e6c chore(deps): add diagram generation tooling`
- `fd247d6 docs(diagrams): add class, project, and control flow diagrams`
