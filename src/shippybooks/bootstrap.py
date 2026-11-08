from dataclasses import dataclass

from .db import get_session
from .domain.events import BookCreated, BookUpdated, OrderCreated, OrderStatusChanged
from .events import NotificationStore
from .events.bus import EventBus
from .events.notifications import (
    BookNotification,
    NotificationDispatcher,
    NotificationHandler,
    OrderConfirmation,
    StatusUpdate,
    StockAlert,
)
from .services import BookRepository, CommandHandler, OrderRepository
from .services.query_handlers import QueryHandler


@dataclass(frozen=True, slots=True)
class AppState:
    """Typed view of the objects attached to `app.state` at startup."""

    cmd_handler: CommandHandler
    query_handler: QueryHandler
    notification_store: NotificationStore


def _build_notification_handler(store: NotificationStore) -> NotificationHandler:
    handler = NotificationHandler()
    for cls in (OrderConfirmation, BookNotification, StockAlert, StatusUpdate):
        handler.register(cls, store.append)
    return handler


def _build_event_bus(dispatcher: NotificationDispatcher) -> EventBus:
    bus = EventBus()
    bus.subscribe(BookCreated, dispatcher.on_book_created)
    bus.subscribe(BookUpdated, dispatcher.on_book_updated)
    bus.subscribe(OrderCreated, dispatcher.on_order_created)
    bus.subscribe(OrderStatusChanged, dispatcher.on_status_changed)
    return bus


def build_app_state() -> AppState:
    """Construct the full object graph."""
    session = next(get_session())
    book_repo = BookRepository(session)
    order_repo = OrderRepository()
    store = NotificationStore()

    dispatcher = NotificationDispatcher(_build_notification_handler(store))
    bus = _build_event_bus(dispatcher)

    return AppState(
        cmd_handler=CommandHandler(bus, book_repo, order_repo),
        query_handler=QueryHandler(book_repo, order_repo),
        notification_store=store,
    )
