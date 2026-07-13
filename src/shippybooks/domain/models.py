"""Domain models for the bookstore application."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


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


class Order(BaseModel):
    """Order domain aggregate."""

    id: str
    items: list[OrderItem] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
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
        self.last_updated = datetime.utcnow()
