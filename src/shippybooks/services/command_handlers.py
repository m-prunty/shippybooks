"""Command handlers for the bookstore application."""

from ..domain import (
    Book,
    BookCreated,
    BookUpdated,
    ChangeOrderStatus,
    Command,
    CreateBook,
    CreateOrder,
    Order,
    OrderCreated,
    OrderStatusChanged,
    UpdateBookStock,
)
from ..events import EventBus, StockAlert


class BookRepository:
    """Repository for managing Book aggregates."""

    def __init__(self) -> None:
        """Initialize the repository with an empty dictionary."""
        self._books: dict[str, Book] = {}

    def get(self, id: str) -> Book:
        """Retrieve a book by its ID."""
        print(self._books)
        print(id)
        return self._books[id]

    def save(self, book: Book) -> None:
        """Save or update a book in the repository."""
        self._books[book.id] = book

    def all(self) -> list[Book]:
        """Return a list of all books in the repository."""
        return list(self._books.values())


class OrderRepository:
    """Repository for managing Order aggregates."""

    def __init__(self) -> None:
        """Initialize the repository with an empty dictionary."""
        self._orders: dict[str, Order] = {}

    def get(self, id: str) -> Order:
        """Retrieve an order by its ID."""
        return self._orders[id]

    def save(self, order: Order) -> None:
        """Save or update an order in the repository."""
        self._orders[order.id] = order

    def all(self) -> list[Order]:
        """Return a list of all orders in the repository."""
        return list(self._orders.values())


class CommandHandler:
    """Handles commands and manages domain aggregates."""

    def __init__(
        self,
        event_bus: EventBus,
        book_repo: BookRepository,
        order_repo: OrderRepository,
    ) -> None:
        """Initialize the command handler with repositories and event bus."""
        self.event_bus = event_bus
        self.book_repo = book_repo
        self.order_repo = order_repo

    def handle(self, command: Command) -> None:
        """Dispatch the command to the appropriate handler method."""
        if isinstance(command, CreateBook):
            self._create_book(command)
        elif isinstance(command, UpdateBookStock):
            self._update_stock(command)
        elif isinstance(command, CreateOrder):
            self._create_order(command)
        elif isinstance(command, ChangeOrderStatus):
            self._change_status(command)

    def _create_book(self, cmd: CreateBook) -> None:
        """Create a new book and publish an event."""
        book = Book(**cmd.__dict__)
        self.book_repo.save(book)
        self.event_bus.publish(BookCreated(book=book))

    def _update_stock(self, cmd: UpdateBookStock) -> None:
        """Update the stock of an existing book and publish an event."""
        book = self.book_repo.get(cmd.id)
        book.update_stock(cmd.quantity)
        self.book_repo.save(book)
        self.event_bus.publish(BookUpdated(book=book))
        if book.stock < 5:
            self.event_bus.publish(StockAlert(book_id=book.id, current_stock=book.stock))

    def _create_order(self, cmd: CreateOrder) -> None:
        """Create a new order, update book stocks, and publish events."""
        order = Order(id=cmd.id)

        for item in cmd.items:
            book = self.book_repo.get(item.book_id)
            order.add_item(book, item.quantity)
            book.update_stock(-item.quantity)
            self.book_repo.save(book)
            self.event_bus.publish(BookUpdated(book=book))

        self.order_repo.save(order)
        self.event_bus.publish(OrderCreated(order=order))

    def _change_status(self, cmd: ChangeOrderStatus) -> None:
        """Change the status of an existing order and publish an event."""
        order = self.order_repo.get(cmd.id)
        old = order.status
        order.change_status(cmd.new_status)
        self.order_repo.save(order)
        self.event_bus.publish(
            OrderStatusChanged(
                order_id=cmd.id, old_status=old, new_status=cmd.new_status
            )
        )
