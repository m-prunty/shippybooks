from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..domain import (
    BookCreated,
    BookUpdated,
    OrderCreated,
    OrderStatus,
    OrderStatusChanged,
)


@dataclass
class Notification:
    @abstractmethod
    def to_event(self) -> dict[str, Any]: ...


@dataclass
class BookNotification(Notification):
    book_id: str
    status: str
    stock: int

    def to_event(self) -> dict[str, Any]:
        return {
            "kind": "book_notification",
            "message": f"Book {self.book_id[:8]} — {self.status} (stock: {self.stock})",
            "book_id": self.book_id,
        }


@dataclass
class OrderConfirmation(Notification):
    order_id: str
    total: float

    def to_event(self) -> dict[str, Any]:
        return {
            "kind": "order_confirmation",
            "message": f"Order #{self.order_id[:8]} confirmed — ${self.total:.2f}",
            "order_id": self.order_id,
        }


@dataclass
class StockAlert(Notification):
    book_id: str
    current_stock: int

    def to_event(self) -> dict[str, Any]:
        return {
            "kind": "stock_alert",
            "message": f"Low stock: {self.current_stock} remaining (book {self.book_id[:8]})",
            "book_id": self.book_id,
            "current_stock": self.current_stock,
        }


@dataclass
class StatusUpdate(Notification):
    order_id: str
    new_status: OrderStatus

    def to_event(self) -> dict[str, Any]:
        return {
            "kind": "status_update",
            "message": f"Order #{self.order_id[:8]} → {self.new_status.value}",
            "order_id": self.order_id,
            "new_status": self.new_status.value,
        }


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
        self.handler.dispatch(
            BookNotification(
                book_id=e.book.id, status="created", stock=e.book.stock
            )
        )

    def on_book_updated(self, e: BookUpdated) -> None:
        if e.book.stock < 5:
            self.handler.dispatch(
                StockAlert(book_id=e.book.id, current_stock=e.book.stock)
            )
        else:
            self.handler.dispatch(
                BookNotification(
                    book_id=e.book.id, status="updated", stock=e.book.stock
                )
            )

    def on_order_created(self, e: OrderCreated) -> None:
        self.handler.dispatch(
            OrderConfirmation(order_id=e.order.id, total=e.order.total)
        )

    def on_status_changed(self, e: OrderStatusChanged) -> None:
        self.handler.dispatch(
            StatusUpdate(order_id=e.order_id, new_status=e.new_status)
        )
