# Event Bus

from .events import EventBus, OrderNotification
from .services import OrderService


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
