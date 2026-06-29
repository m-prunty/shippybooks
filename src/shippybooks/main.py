"""CQRS Notification System — application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints import books_router, orders_router
from .api.endpoints.notifications import router as notifications_router
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
    handler = NotificationHandler()
    for cls in (OrderConfirmation, BookNotification, StockAlert, StatusUpdate):
        handler.register(cls, store.append)
        print(f"Registered {cls.__name__} → store.append")  # temporary
    return handler


def create_app() -> FastAPI:
    book_repo = BookRepository()
    order_repo = OrderRepository()
    store = NotificationStore()  # new

    notify_handler = _build_notification_handler(store)  # updated signature
    dispatcher = NotificationDispatcher(notify_handler)
    bus = _build_event_bus(dispatcher)
    cmd_handler = CommandHandler(bus, book_repo, order_repo)
    query_handler = QueryHandler(book_repo, order_repo)

    app = FastAPI(title="CQRS Notification System")
    app.state.cmd_handler = cmd_handler
    app.state.query_handler = query_handler
    app.state.notification_store = store  # new

    app.include_router(books_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")
    app.include_router(notifications_router, prefix="/api/v1")  # new

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


def _build_event_bus(dispatcher: NotificationDispatcher) -> EventBus:
    """Wire domain events to their notification dispatcher methods."""
    bus = EventBus()
    bus.subscribe(BookCreated, dispatcher.on_book_created)
    bus.subscribe(BookUpdated, dispatcher.on_book_updated)
    bus.subscribe(OrderCreated, dispatcher.on_order_created)
    bus.subscribe(OrderStatusChanged, dispatcher.on_status_changed)
    return bus


# Module-level instance required by uvicorn's string reference with reload=True
app = create_app()


def main() -> None:
    """Start the uvicorn server."""
    import uvicorn

    uvicorn.run("shippybooks.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
