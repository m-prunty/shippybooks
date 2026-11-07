"""Events module."""

from .bus import (
    EventBus,
)
from .notifications import (
    BookNotification,
    Notification,
    NotificationDispatcher,
    NotificationHandler,
    OrderConfirmation,
    StatusUpdate,
    StockAlert,
)
from .store import NotificationStore

__all__ = []

__all__ += [
    "EventBus",
]

__all__ += [
    "NotificationStore",
]

__all__ += [
    "BookNotification",
    "Notification",
    "NotificationDispatcher",
    "NotificationHandler",
    "OrderConfirmation",
    "StatusUpdate",
    "StockAlert",
]


"""from .bus import EventBus
from .handlers import AuditHandler, OrderHandler, StockHandler

__all__ = [
    "EventBus",
    "OrderNotification",
    "AuditHandler",
    "OrderHandler",
    "StockHandler",
]
"""
