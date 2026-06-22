from dataclasses import dataclass

from .models import OrderStatus


@dataclass
class Command:
    pass


@dataclass
class CreateBook(Command):
    id: str
    title: str
    author: str
    price: float
    stock: int


@dataclass
class UpdateBookStock(Command):
    id: str
    quantity: int


@dataclass
class CreateOrder(Command):
    id: str
    items: list[tuple[str, int]]


@dataclass
class ChangeOrderStatus(Command):
    id: str
    new_status: OrderStatus
