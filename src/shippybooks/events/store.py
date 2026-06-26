import threading
from typing import Any

from .notifications import Notification


class NotificationStore:
    """Thread-safe append-only notification log.

    Synchronous command handlers write; async SSE endpoint reads.
    IDs are sequential integers — used as SSE event IDs for reconnection.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: list[dict[str, Any]] = []

    def append(self, notification: Notification) -> None:
        with self._lock:
            event_id = len(self._events)
            self._events.append({"id": event_id, **notification.to_event()})

    def since(self, last_id: int) -> list[dict[str, Any]]:
        """Return all events after last_id. Pass -1 for all events."""
        with self._lock:
            return list(self._events[last_id + 1 :])
