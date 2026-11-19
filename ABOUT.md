# What is this?

**shippybooks** is a CQRS (Command Query Responsibility Segregation) implementation for a book store. It is a small FastAPI application that separates write operations (commands) from read operations (queries) and uses an event-driven notification store to propagate changes.

The project provides REST API endpoints for:

- **Books** — create books (`POST /api/v1/books/`), update stock (`POST /api/v1/books/{book_id}/stock/`), retrieve a book (`GET /api/v1/books/{book_id}`), and list all books (`GET /api/v1/books/`).
- **Orders** — create orders (`POST /api/v1/orders/`), change an order's status (`POST /api/v1/orders/{order_id}/status/`), retrieve an order (`GET /api/v1/orders/{order_id}`), and list all orders (`GET /api/v1/orders/`).
- **Notifications** — stream notification events from `GET /api/v1/notifications/stream` using server-sent events.
- **Health** — query the liveness, readiness, and aggregate diagnostic endpoints at `/health/live`, `/health/ready`, and `/health`.

The domain model is split into two sides:

- **Command side** (`src/shippybooks/domain/commands.py`) — immutable Pydantic commands such as `CreateBook`, `UpdateBookStock`, `CreateOrder`, and `ChangeOrderStatus`, handled by command handlers in `services/command_handlers.py`.
- **Query side** (`src/shippybooks/domain/queries.py`) — read models and query handlers in `services/query_handlers.py` that read directly from the repository.

The repository layer supports optional SQLAlchemy-backed persistence. The ORM models (`BookORM`, `OrderORM`, `OrderItemORM`) and SQLite engine live under `src/shippybooks/db/`, while `settings.persistent_memory` controls whether repositories use the ORM path. In-memory repositories remain the default runtime behavior.

Commands publish events through the in-process event bus in `events/bus.py`. Notification handlers enrich those events and append them to the in-memory `NotificationStore` in `events/store.py`; a durable transactional outbox or append-only event store is not currently implemented.

The application object graph is built in `bootstrap.py`, exposed through `main.py` (the FastAPI factory and uvicorn entry point), and configured through `settings.py`.

# Why?

This project was built to explore and practice the CQRS pattern — separating the write model from the read model so each can be optimized independently. Commands mutate state and publish events; queries read projected state without touching the command stack.

Specific motivations:

- **Learn CQRS in Python** — following the Arjan Codes CQRS tutorial and related materials on event-driven architecture.
- **Explore event-driven notifications** — propagating domain changes to subscribers without coupling HTTP handlers to notification delivery.
- **Experiment with persistence** — adding an optional SQLAlchemy repository path while retaining an in-memory mode for simple local runs and tests.
- **Build a reference implementation** — a small but complete book-store domain with commands, queries, repositories, an event bus, a notification store, and a FastAPI HTTP layer.

The `README.md` collects the reference articles and tutorials used while building this project.
