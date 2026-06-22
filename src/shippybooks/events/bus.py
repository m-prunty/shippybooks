from collections.abc import Callable

from ..domain import DomainEvent


class EventBus:
    """Synchronous in-process event bus with failure boundaries."""

    def __init__(self) -> None:
        self._subscribers: dict[type[DomainEvent], list[Callable]] = {}

    def subscribe(
        self, event_type: type[DomainEvent], handler: Callable
    ) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._subscribers.get(type(event), []):
            try:
                handler(event)
            except Exception as e:
                print(f"Event handler failed: {e}")


"""

class EventBus:
    subscribers = {}

    @classmethod
    def subscribe(cls, event_type, subscriber):
        if event_type not in cls.subscribers:
            cls.subscribers[event_type] = []
        cls.subscribers[event_type].append(subscriber)

    @classmethod
    def publish(cls, event_type, data=None):
        if event_type in cls.subscribers:
            for subscriber in cls.subscribers[event_type]:
                subscriber.handle_event(event_type, data)
"""
