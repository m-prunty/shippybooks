"""CQRS Notification System — application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import AppState, books_router, notifications_router, orders_router
from .domain.events import (
    BookCreated,
    BookUpdated,
    OrderCreated,
    OrderStatusChanged,
)
from .events import NotificationStore  # add to imports
from .events.bus import EventBus
from .events.notifications import (
    BookNotification,
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


def _build_notification_handler(
    store: NotificationStore,
) -> NotificationHandler:
    """Wire notification event classes to the store's append method."""
    handler = NotificationHandler()
    for cls in (OrderConfirmation, BookNotification, StockAlert, StatusUpdate):
        handler.register(cls, store.append)
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
    """Construct and wire the FastAPI application."""
    book_repo = BookRepository()
    order_repo = OrderRepository()
    store = NotificationStore()

    notify_handler = _build_notification_handler(store)
    dispatcher = NotificationDispatcher(notify_handler)
    bus = _build_event_bus(dispatcher)
    cmd_handler = CommandHandler(bus, book_repo, order_repo)
    query_handler = QueryHandler(book_repo, order_repo)

    app = FastAPI(title="CQRS Notification System")
    app.state.app_state = AppState(
        cmd_handler=cmd_handler,
        query_handler=query_handler,
        notification_store=store,
    )

    app.include_router(books_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")
    app.include_router(notifications_router, prefix="/api/v1")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://mprunty.com",
            "https://www.mprunty.com",
            "http://localhost:5173",
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
