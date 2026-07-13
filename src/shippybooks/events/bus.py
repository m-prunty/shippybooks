from collections.abc import Callable

from ..domain import DomainEvent


class EventBus:
    """Synchronous in-process event bus with failure boundaries."""

    def __init__(self) -> None:
        """Initialize the event bus with an empty subscriber dictionary."""
        self._subscribers: dict[
            type[DomainEvent], list[Callable[..., None]]
        ] = {}

    def subscribe(
        self, event_type: type[DomainEvent], handler: Callable[..., None]
    ) -> None:
        """Subscribe a handler to a specific event type."""
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribed handlers."""
        for handler in self._subscribers.get(type(event), []):
            try:
                handler(event)
            except Exception as e:
                print(f"Event handler failed: {e}")
