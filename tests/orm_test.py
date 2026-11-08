from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from shippybooks.db.base import Base
from shippybooks.db.models import BookORM, OrderItemORM, OrderORM
from shippybooks.domain import Book, Order, OrderItem, OrderStatus
from shippybooks.services import BookRepository, OrderRepository


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    _ = (BookORM, OrderORM, OrderItemORM)
    return sessionmaker(engine, expire_on_commit=False)()


def test_book_repository_persists_and_reads() -> None:
    session = _session()
    repo = BookRepository(session)
    book = Book(id="b1", title="Test", author="Author", price=12.5, stock=10)

    repo.save(book)

    saved = repo.get("b1")
    assert saved.title == "Test"
    assert len(repo.all()) == 1


def test_order_repository_persists_items_and_status() -> None:
    session = _session()
    book_repo = BookRepository(session)
    order_repo = OrderRepository(session)

    book_repo.save(Book(id="b1", title="Test", author="Author", price=5.0, stock=10))
    order = Order(
        id="o1",
        items=[OrderItem(book_id="b1", quantity=2)],
        timestamp=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        status=OrderStatus.PENDING,
        total=10.0,
    )
    order_repo.save(order)

    loaded = order_repo.get("o1")
    assert loaded.total == 10.0
    assert loaded.items[0].book_id == "b1"

    loaded.change_status(OrderStatus.PROCESSING)
    order_repo.save(loaded)
    assert order_repo.get("o1").status == OrderStatus.PROCESSING
