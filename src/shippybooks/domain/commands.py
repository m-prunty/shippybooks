from dataclasses import dataclass

from pydantic import BaseModel

from .models import OrderStatus


class Command(BaseModel):
    pass


class CreateBook(Command):
    id: str
    title: str
    author: str
    price: float
    stock: int


class UpdateBookStock(Command):
    id: str
    quantity: int


class CreateOrder(Command):
    id: str
    items: list[tuple[str, int]]


@dataclass
class ChangeOrderStatus(Command):
    id: str
    new_status: OrderStatus
