from dataclasses import field
from enum import Enum

from pydantic import BaseModel


class OrderStatus(Enum):
    """Order status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class Book(BaseModel):
    """Book domain aggregate."""

    id: str
    title: str
    author: str
    price: float
    stock: int

    def update_stock(self, quantity: int) -> None:
        """Update book stock by quantity."""
        self.stock += quantity


class OrderItem(BaseModel):
    """Order item value object."""

    book_id: str
    quantity: int
    price: float


class Order(BaseModel):
    """Order domain aggregate."""

    id: str
    items: list[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    total: float = 0.0

    def add_item(self, book: Book, quantity: int) -> None:
        """Add item to order and update total."""
        item = OrderItem(book_id=book.id, quantity=quantity, price=book.price)
        self.items.append(item)
        self.total += book.price * quantity

    def change_status(self, new_status: OrderStatus) -> None:
        """Change order status."""
        self.status = new_status


"""
@dataclass
class Book:
    book_key: int
    title: str
    stock: int

    def change_stock(self, amount):
        self.stock += amount
        EventBus.publish(
            "StockChanged", {"book_id": self.id, "new_stock": self.stock}
        )


class OrderStatus(Enum):
    PENDING = "Pending"
    PLACED = "Placed"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"


@dataclass
class Order:
    order_key: int
    book_key: int
    qty: int
    status: OrderStatus = OrderStatus.PENDING

    def place_order(self):
        self.status = OrderStatus.PLACED
        EventBus.publish(
            "OrderPlaced",
            {"order_id": self.order_key, "book_id": self.book_key},
        )

    def fulfill_order(self):
        self.status = OrderStatus.SHIPPED
        EventBus.publish(
            "OrderShipped",
            {"order_id": self.order_key, "book_id": self.book_key},
        )


@dataclass
class Customer:
    key: int
    name: str
    contact_info: str


@dataclass
class Notification:
    message: str
    """
