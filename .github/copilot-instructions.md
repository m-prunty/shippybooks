# Copilot Instructions for `shippybooks`

## Build, test, and lint commands

Prefer the existing `Makefile` targets (they wrap `uv` commands):

- Install dependencies: `make install`
- Install production deps only: `make install-prod`
- Run the app (local dev): `make run`
- Run all tests: `make test`
- Run a single test: `uv run pytest tests/cqrs_test.py::test_create_book_command`
- Type-check/lint: `make lint`

Equivalent direct commands from current project config:

- `uv sync`
- `uv sync --frozen --no-dev`
- `uv run uvicorn shippybooks.main:app --reload`
- `uv run pytest`
- `uv run mypy --strict src`

## High-level architecture

This repository implements a CQRS-style bookstore service with FastAPI, in-process domain events, and SSE notifications.

1. `src/shippybooks/main.py` is the FastAPI composition root. It constructs the application, registers the health router at the root, and registers the books, orders, and notifications routers under `/api/v1`.
2. `src/shippybooks/bootstrap.py` builds the application object graph: repositories, command/query handlers, event bus subscriptions, notification dispatcher/handler, and the shared notification store.
3. API endpoints in `src/shippybooks/api/endpoints/` translate HTTP payloads into commands/queries and delegate to injected handlers via typed dependencies from `src/shippybooks/api/dependencies.py`.
4. The write side is in `src/shippybooks/services/command_handlers.py`: command handling mutates aggregates and publishes domain events.
5. The read side is in `src/shippybooks/services/query_handlers.py`: query handling reads aggregate state from repositories.
6. Domain events (`src/shippybooks/domain/events.py`) are dispatched by `src/shippybooks/events/bus.py` to notification mapping logic in `src/shippybooks/events/notifications.py`.
7. Notifications are appended to `NotificationStore` (`src/shippybooks/events/store.py`) and streamed to clients via `GET /api/v1/notifications/stream` (`src/shippybooks/api/endpoints/notifications.py`) using SSE IDs and `last-event-id` resume behavior.
8. Operational probes are implemented in `src/shippybooks/api/endpoints/health.py`: `/health/live`, `/health/ready`, and `/health`.

## Key repository conventions

- Command classes in `domain/commands.py` are immutable Pydantic `BaseModel` subclasses configured with `ConfigDict(frozen=True)`.
- Query classes in `domain/queries.py` are Pydantic `BaseModel` subclasses and are dispatched by explicit `isinstance(...)` checks in handlers.
- Shared app services are stored as a typed `AppState` object on `app.state` and accessed through dependency aliases (`CmdHandlerDep`, `QueryHandlerDep`, `NotificationStoreDep`).
- Notification payloads come from `Notification.to_event()` and are enriched in `NotificationStore` with sequential numeric IDs used as SSE event IDs.
- Low-stock alert behavior is tied to a hard threshold of `stock < 5` in command/notification flow.
- SQLAlchemy setup exists under `src/shippybooks/db/`, but current runtime behavior uses in-memory repositories in `src/shippybooks/services/repos.py`; changes to persistence should account for this split.

## Project documentation

- `README.md` links to the project overview and collects the CQRS/event-driven reference material.
- `ABOUT.md` describes the implemented architecture, persistence behavior, and project motivations.
- No `CONTRIBUTING.md` or other assistant-rule files (`CLAUDE.md`, `.cursorrules`, `AGENTS.md`, `.windsurfrules`, `CONVENTIONS.md`, `.clinerules`, etc.) are present.
