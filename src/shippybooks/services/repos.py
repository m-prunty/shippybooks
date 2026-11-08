from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from ..db import BookORM, OrderORM
from ..domain import Book, Order
from ..settings import settings


class BookRepository:
    """Repository for managing Book aggregates."""

    def __init__(self, session: Session = None) -> None:
        """Initialize the repository with an empty dictionary."""
        self._books: dict[str, Book] = {}
        if session:
            self.persistent_memory = settings.persistent_memory
            self.session = session

    def get(self, id: str) -> Book:
        if self.persistent_memory:
            try:
                orm = self.session.query(BookORM).filter_by(id=id).one()
                return orm.to_domain()
            except NoResultFound:
                raise KeyError(f"Book with id {id} not found")
        else:
            return self._books[id]

    def save(self, book: Book) -> None:
        if self.persistent_memory:
            orm = self.session.query(BookORM).filter_by(id=book.id).first()
            if orm:
                orm.update_from_domain(book)
            else:
                orm = BookORM(**book.dict())
                self.session.add(book_orm)
            self.session.commit()
        else:
            self._books[book.id] = book

    def all(self) -> list[Book]:
        if self.persistent_memory:
            return [orm.to_domain() for orm in self.session.query(BookORM).all()]
        else:
            return list(self._books.values())


#    def get(self, id: str) -> Book:
#        """Retrieve a book by its ID."""
#        return self._books[id]
#
#    def save(self, book: Book) -> None:
#        """Save or update a book in the repository."""
#        self._books[book.id] = book
#
#    def all(self) -> list[Book]:
#        """Return a list of all books in the repository."""
#        return list(self._books.values())


class OrderRepository:
    """Repository for managing Order aggregates."""

    def __init__(self, session: Session | None = None) -> None:
        """Initialize the repository with an empty dictionary."""
        self._orders: dict[str, Order] = {}
        if session:
            self.persistent_memory = settings.persistent_memory
            self.session = session

    def get(self, id: str) -> Order:
        if self.persistent_memory:
            try:
                orm = self.session.query(OrderORM).filter_by(id=id).one()
                return orm.to_domain()
            except NoResultFound:
                raise KeyError(f"order with id {id} not found")
        else:
            return self._orders[id]

    def save(self, order: Order) -> None:
        if self.persistent_memory:
            orm = self.session.query(OrderORM).filter_by(id=order.id).first()
            if orm:
                orm.update_from_domain(order)
            else:
                orm = OrderORM(**order.dict())
                self.session.add(orm)
            self.session.commit()
        else:
            self._orders[order.id] = order

    def all(self) -> list[Order]:
        if self.persistent_memory:
            return [orm.to_domain() for orm in self.session.query(OrderORM).all()]
        else:
            return list(self._orders.values())
