from domain.commands import (
    ChangeOrderStatus,
    Command,
    CreateBook,
    CreateOrder,
    UpdateBookStock,
)
from domain.events import (
    BookCreated,
    BookUpdated,
    OrderCreated,
    OrderStatusChanged,
)
from domain.models import Book, Order
from events.bus import EventBus


class BookRepository:
    def __init__(self) -> None:
        self._books: dict[str, Book] = {}

    def get(self, id: str) -> Book:
        return self._books[id]

    def save(self, book: Book) -> None:
        self._books[book.id] = book

    def all(self) -> list[Book]:
        return list(self._books.values())


class OrderRepository:
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def get(self, id: str) -> Order:
        return self._orders[id]

    def save(self, order: Order) -> None:
        self._orders[order.id] = order

    def all(self) -> list[Order]:
        return list(self._orders.values())


class CommandHandler:
    def __init__(
        self,
        event_bus: EventBus,
        book_repo: BookRepository,
        order_repo: OrderRepository,
    ) -> None:
        self.event_bus = event_bus
        self.book_repo = book_repo
        self.order_repo = order_repo

    def handle(self, command: Command) -> None:
        if isinstance(command, CreateBook):
            self._create_book(command)
        elif isinstance(command, UpdateBookStock):
            self._update_stock(command)
        elif isinstance(command, CreateOrder):
            self._create_order(command)
        elif isinstance(command, ChangeOrderStatus):
            self._change_status(command)

    def _create_book(self, cmd: CreateBook) -> None:
        book = Book(**cmd.__dict__)
        self.book_repo.save(book)
        self.event_bus.publish(BookCreated(book=book))

    def _update_stock(self, cmd: UpdateBookStock) -> None:
        book = self.book_repo.get(cmd.id)
        book.update_stock(cmd.quantity)
        self.book_repo.save(book)
        self.event_bus.publish(BookUpdated(book=book))

    def _create_order(self, cmd: CreateOrder) -> None:
        order = Order(id=cmd.id)
        for book_id, qty in cmd.items:
            book = self.book_repo.get(book_id)
            order.add_item(book, qty)
            book.update_stock(-qty)
            self.book_repo.save(book)
            self.event_bus.publish(BookUpdated(book=book))
        self.order_repo.save(order)
        self.event_bus.publish(OrderCreated(order=order))

    def _change_status(self, cmd: ChangeOrderStatus) -> None:
        order = self.order_repo.get(cmd.id)
        old = order.status
        order.change_status(cmd.new_status)
        self.order_repo.save(order)
        self.event_bus.publish(
            OrderStatusChanged(
                order_id=cmd.id, old_status=old, new_status=cmd.new_status
            )
        )
