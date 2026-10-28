"""Notification system for the bookstore application."""

from abc import ABC,abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from ..domain import (
    BookCreated,
    BookUpdated,
    OrderCreated,
    OrderStatus,
    OrderStatusChanged,
)


class Message(StrEnum):
    """Message templates for notifications."""

    BOOK_NOTIFICATION = "Book {0} has been {1}. Current stock: {2}"
    ORDER_CONFIRMATION = "Order {0} confirmed. Total: ${1:.2f}"
    STOCK_ALERT = "Low stock alert for book {0}. Current stock: {1}"
    STATUS_UPDATE = "Order {0} status updated to {1}"


@dataclass(frozen=True, slots=True)
class Notification(ABC):
    """Base class for notifications."""

    @abstractmethod
    def to_event(self) -> dict[str, Any]: ...


@dataclass(frozen=True, slots=True)
class BookNotification(Notification):
    """Notification for book creation or update."""

    book_id: str
    status: str
    stock: int

    def to_event(self) -> dict[str, Any]:
        """Convert the book notification to an event dictionary."""
        return {
            "kind": "book_notification",
            "message": Message.BOOK_NOTIFICATION.format(
                self.book_id, self.status, self.stock
            ),
            "book_id": self.book_id,
        }


@dataclass(frozen=True, slots=True)
class OrderConfirmation(Notification):
    """Notification for order confirmation."""

    order_id: str
    total: float

    def to_event(self) -> dict[str, Any]:
        """Convert the order confirmation notification to an event dict."""
        return {
            "kind": "order_confirmation",
            "message": Message.ORDER_CONFIRMATION.format(
                self.order_id, self.total
            ),
            "order_id": self.order_id,
        }


@dataclass(frozen=True, slots=True)
class StockAlert(Notification):
    """Notification for low stock alert."""

    book_id: str
    current_stock: int

    def to_event(self) -> dict[str, Any]:
        """Convert the stock alert notification to an event dictionary."""
        return {
            "kind": "stock_alert",
            "message": Message.STOCK_ALERT.format(
                self.book_id, self.current_stock
            ),
            "book_id": self.book_id,
            "current_stock": self.current_stock,
        }



@dataclass(frozen=True, slots=True)
class StatusUpdate(Notification):
    """Notification for order status update."""

    order_id: str
    new_status: OrderStatus

    def to_event(self) -> dict[str, Any]:
        return {
            "kind": "status_update",
            "message": Message.STATUS_UPDATE.format(
                self.order_id, self.new_status.value
            ),
            "order_id": self.order_id,
            "new_status": self.new_status.value,
        }


class NotificationHandler:
    def __init__(self) -> None:
        self._handlers: dict[
            type[Notification], list[Callable[[Notification], None]]
        ] = {}

    def register(
        self,
        notify_type: type[Notification],
        handler: Callable[[Notification], None],
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
