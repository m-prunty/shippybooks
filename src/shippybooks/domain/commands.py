"""Commands for the bookstore application."""

from pydantic import BaseModel, ConfigDict

from .models import OrderItem, OrderStatus


class Command(BaseModel):
    """Base class for commands."""

    model_config = ConfigDict(frozen=True)


class CreateBook(Command):
    """Command to create a new book."""

    id: str
    title: str
    author: str
    price: float
    stock: int


class UpdateBookStock(Command):
    """Command to update the stock of a book."""

    id: str
    quantity: int


class CreateOrder(Command):
    """Command to create a new order."""

    id: str
    items: list[OrderItem]


class ChangeOrderStatus(Command):
    """Command to change the status of an order."""

    id: str
    new_status: OrderStatus
