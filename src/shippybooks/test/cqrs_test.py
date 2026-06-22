"""Pytest-based test suite for CQRS system."""

import pytest

from ..domain import (
    Book,
    BookCreated,
    CreateBook,
    CreateOrder,
    GetBook,
    ListBooks,
    Order,
    UpdateBookStock,
)
from ..events import (
    EventBus,
    NotificationDispatcher,
    NotificationHandler,
    StockAlert,
)
from ..services import (
    BookRepository,
    CommandHandler,
    OrderRepository,
    QueryHandler,
)


@pytest.fixture
def system():
    bus = EventBus()
    br, or_ = BookRepository(), OrderRepository()
    return bus, br, or_, CommandHandler(bus, br, or_), QueryHandler(br, or_)


def test_domain_aggregates():
    book = Book(id="1", title="T", author="A", price=10.0, stock=100)
    book.update_stock(-10)
    assert book.stock == 90

    order = Order(id="o1")
    order.add_item(book, 2)
    assert order.total == 20.0
    assert len(order.items) == 1


def test_command_flow(system):
    bus, br, or_, ch, qh = system
    ch.handle(
        CreateBook(id="b1", title="T", author="A", price=10.0, stock=100)
    )
    assert br.get("b1").title == "T"
    ch.handle(UpdateBookStock(id="b1", quantity=-5))
    assert br.get("b1").stock == 95


def test_order_workflow(system):
    bus, br, or_, ch, qh = system
    br.save(Book(id="b1", title="T", author="A", price=10.0, stock=100))
    ch.handle(CreateOrder(id="o1", items=[("b1", 3)]))
    assert or_.get("o1").total == 30.0
    assert br.get("b1").stock == 97


def test_query_side(system):
    bus, br, or_, ch, qh = system
    br.save(Book(id="b1", title="T", author="A", price=10.0, stock=100))
    assert len(qh.handle(ListBooks())) == 1
    assert qh.handle(GetBook(id="b1")).title == "T"


def test_notifications(system):
    bus, br, or_, ch, qh = system
    nh = NotificationHandler()
    dispatcher = NotificationDispatcher(nh)
    bus.subscribe(BookCreated, dispatcher.on_book_created)
    bus.subscribe(
        StockAlert,
        lambda e: nh.dispatch(
            StockAlert(book_id=e.book.id, current_stock=e.book.stock)
        ),
    )

    alerts = []
    nh.register(StockAlert, lambda n: alerts.append(n.book_id))
    ch.handle(CreateBook(id="b1", title="T", author="A", price=10.0, stock=3))
    ch.handle(UpdateBookStock(id="b1", quantity=-1))
    assert len(alerts) == 1


if __name__ == "__main__":
    pytest.main()
