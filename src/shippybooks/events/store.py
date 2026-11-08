from typing import Any

from .notifications import Notification


class NotificationStore:
    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def append(self, notification: Notification) -> None:
        event_id = len(self._events)
        self._events.append({"id": event_id, **notification.to_event()})

    def since(self, last_id: int) -> list[dict[str, Any]]:
        """Return all events after last_id. Pass -1 for all events."""
        return list(self._events[last_id + 1 :])
