from dataclasses import dataclass

from .models import Book, Order, OrderStatus


@dataclass
class DomainEvent:
    pass


@dataclass
class BookCreated(DomainEvent):
    book: Book


@dataclass
class BookUpdated(DomainEvent):
    book: Book


@dataclass
class OrderCreated(DomainEvent):
    order: Order


@dataclass
class OrderStatusChanged(DomainEvent):
    order_id: str
    old_status: OrderStatus
    new_status: OrderStatus
