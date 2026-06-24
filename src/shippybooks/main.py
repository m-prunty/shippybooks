"""CQRS Notification System — application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints import books_router, orders_router
from .domain.events import (
    BookCreated,
    BookUpdated,
    OrderCreated,
    OrderStatusChanged,
)
from .events.bus import EventBus
from .events.notifications import (
    NotificationDispatcher,
    NotificationHandler,
    OrderConfirmation,
    StatusUpdate,
    StockAlert,
)
from .services.command_handlers import (
    BookRepository,
    CommandHandler,
    OrderRepository,
)
from .services.query_handlers import QueryHandler


def _build_notification_handler() -> NotificationHandler:
    """Register console sinks for each notification type."""
    handler = NotificationHandler()
    handler.register(
        OrderConfirmation,
        lambda n: print(f"Order confirmed: {n.order_id} (${n.total:.2f})"),
    )
    handler.register(
        StockAlert,
        lambda n: print(
            f"Low stock alert: {n.book_id} ({n.current_stock} remaining)"
        ),
    )
    handler.register(
        StatusUpdate,
        lambda n: print(
            f"Status update: {n.order_id} -> {n.new_status.value}"
        ),
    )
    return handler


def _build_event_bus(dispatcher: NotificationDispatcher) -> EventBus:
    """Wire domain events to their notification dispatcher methods."""
    bus = EventBus()
    bus.subscribe(BookCreated, dispatcher.on_book_created)
    bus.subscribe(BookUpdated, dispatcher.on_book_updated)
    bus.subscribe(OrderCreated, dispatcher.on_order_created)
    bus.subscribe(OrderStatusChanged, dispatcher.on_status_changed)
    return bus


def create_app() -> FastAPI:
    """Assemble and return the configured FastAPI application."""
    book_repo = BookRepository()
    order_repo = OrderRepository()

    notify_handler = _build_notification_handler()
    dispatcher = NotificationDispatcher(notify_handler)
    bus = _build_event_bus(dispatcher)

    cmd_handler = CommandHandler(bus, book_repo, order_repo)
    query_handler = QueryHandler(book_repo, order_repo)

    app = FastAPI(title="CQRS Notification System")
    app.state.cmd_handler = cmd_handler
    app.state.query_handler = query_handler
    app.include_router(books_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://mprunty.com",
            "https://www.mprunty.com",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


# Module-level instance required by uvicorn's string reference with reload=True
app = create_app()


def main() -> None:
    """Start the uvicorn server."""
    import uvicorn

    uvicorn.run("shippybooks.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
