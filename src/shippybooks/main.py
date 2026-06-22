# Event Bus

"""FastAPI endpoints + minimal Django setup."""

from fastapi import FastAPI

from .api.endpoints import books_router, orders_router
from .events.bus import EventBus
from .events.notifications import (
    BookCreated,
    BookUpdated,
    NotificationDispatcher,
    NotificationHandler,
    OrderConfirmation,
    OrderCreated,
    OrderStatusChanged,
    StatusUpdate,
    StockAlert,
)
from .services.command_handlers import (
    BookRepository,
    CommandHandler,
    OrderRepository,
)
from .services.query_handlers import QueryHandler

# Initialize system
bus = EventBus()
book_repo = BookRepository()
order_repo = OrderRepository()
cmd_handler = CommandHandler(bus, book_repo, order_repo)
query_handler = QueryHandler(book_repo, order_repo)
notify_handler = NotificationHandler()
dispatcher = NotificationDispatcher(notify_handler)

# Subscribe events to notifications
bus.subscribe(BookCreated, dispatcher.on_book_created)
bus.subscribe(BookUpdated, dispatcher.on_book_updated)
bus.subscribe(OrderCreated, dispatcher.on_order_created)
bus.subscribe(OrderStatusChanged, dispatcher.on_status_changed)

# Register notification handlers (e.g., logging)
notify_handler.register(
    OrderConfirmation,
    lambda n: print(f"Order confirmed: {n.order_id} (${n.total})"),
)
notify_handler.register(
    StockAlert,
    lambda n: print(f"Low stock: {n.book_id} ({n.current_stock} left)"),
)
notify_handler.register(
    StatusUpdate,
    lambda n: print(f"Status update: {n.order_id} -> {n.new_status.value}"),
)

app = FastAPI(title="CQRS Notification System")

app.state.cmd_handler = cmd_handler
app.state.query_handler = query_handler

app.include_router(books_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
def main():
    # Creating instances
    order_notification_subscriber = OrderNotification()
    order_service = OrderService()

    # Subscribing the subscriber to the 'OrderPlaced' event
    EventBus.subscribe("OrderPlaced", order_notification_subscriber)

    # Placing an order
    order_service.place_order(order_id=123)


if __name__ == "__main__":
    main()
    """
