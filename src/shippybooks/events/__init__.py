"""Events module."""

from .bus import (
    EventBus,
)
from .notifications import (
    Notification,
    NotificationDispatcher,
    NotificationHandler,
    OrderConfirmation,
    StatusUpdate,
    StockAlert,
)

__all__ = []

__all__ += [
    "EventBus",
]

__all__ += [
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
