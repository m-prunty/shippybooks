from ..events import EventBus


class OrderService:
    def place_order(self, order_id):
        # Order placement logic here
        # ...

        # Notify subscribers about the order placement
        EventBus.publish("OrderPlaced", {"order_id": order_id})
