from pydantic import BaseModel

from .models import Book, Order, OrderStatus


class DomainEvent(BaseModel):
    """Base class for domain events."""



class BookCreated(DomainEvent):
    """Event triggered when a new book is created."""

    book: Book


class BookUpdated(DomainEvent):
    """Event triggered when a book is updated."""

    book: Book


class OrderCreated(DomainEvent):
    """Event triggered when a new order is created."""

    order: Order


class OrderStatusChanged(DomainEvent):
    """Event triggered when an order's status is changed."""

    order_id: str
    old_status: OrderStatus
    new_status: OrderStatus
