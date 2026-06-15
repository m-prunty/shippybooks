class OrderNotification:
    def handle_event(self, event_type, data=None):
        if event_type == "OrderPlaced":
            print(
                "Notification: Your order with ID {} has been placed!".format(
                    data["order_id"]
                )
            )
