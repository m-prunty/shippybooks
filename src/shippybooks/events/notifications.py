from collections.abc import Callable
from dataclasses import dataclass

from ..domain import (
    BookCreated,
    BookUpdated,
    OrderCreated,
    OrderStatus,
    OrderStatusChanged,
)


@dataclass
class Notification:
    pass


@dataclass
class OrderConfirmation(Notification):
    order_id: str
    total: float


@dataclass
class StockAlert(Notification):
    book_id: str
    current_stock: int


@dataclass
class StatusUpdate(Notification):
    order_id: str
    new_status: OrderStatus


class NotificationHandler:
    def __init__(self) -> None:
        self._handlers: dict[type[Notification], list[Callable]] = {}

    def register(
        self, notify_type: type[Notification], handler: Callable
    ) -> None:
        self._handlers.setdefault(notify_type, []).append(handler)

    def dispatch(self, notification: Notification) -> None:
        for handler in self._handlers.get(type(notification), []):
            try:
                handler(notification)
            except Exception as e:
                print(f"Notification failed: {e}")


class NotificationDispatcher:
    def __init__(self, handler: NotificationHandler) -> None:
        self.handler = handler

    def on_book_created(self, e: BookCreated) -> None:
        pass

    def on_book_updated(self, e: BookUpdated) -> None:
        if e.book.stock < 5:
            self.handler.dispatch(
                StockAlert(book_id=e.book.id, current_stock=e.book.stock)
            )

    def on_order_created(self, e: OrderCreated) -> None:
        self.handler.dispatch(
            OrderConfirmation(order_id=e.order.id, total=e.order.total)
        )

    def on_status_changed(self, e: OrderStatusChanged) -> None:
        self.handler.dispatch(
            StatusUpdate(order_id=e.order_id, new_status=e.new_status)
        )
