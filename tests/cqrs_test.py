"""Pytest-based test suite for the CQRS system."""

import pytest

from shippybooks.domain import (
    Book,
    BookCreated,
    CreateBook,
    CreateOrder,
    GetBook,
    ListBooks,
    Order,
    OrderItem,
    UpdateBookStock,
)
from shippybooks.events import (
    EventBus,
    NotificationDispatcher,
    NotificationHandler,
    StockAlert,
)
from shippybooks.services import (
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


def make_book(id="b1", stock=100, price=10.0):
    return Book(id=id, title="T", author="A", price=price, stock=stock)


def create_book_cmd(id="b1", stock=100, price=10.0):
    return CreateBook(id=id, title="T", author="A", price=price, stock=stock)


# --- Domain ---------------------------------------------------------------


@pytest.mark.parametrize("delta, expected", [(5, 105), (-10, 90)])
def test_book_update_stock(delta, expected):
    book = make_book()
    book.update_stock(delta)
    assert book.stock == expected


def test_order_add_item():
    book = make_book()
    order = Order(id="o1")
    order.add_item(book, 2)
    assert order.total == 20.0
    assert len(order.items) == 1


# --- Commands -------------------------------------------------------------


def test_create_book_command(system):
    bus, br, or_, ch, qh = system
    ch.handle(create_book_cmd())
    assert br.get("b1").title == "T"


@pytest.mark.parametrize("delta, expected", [(5, 105), (-5, 95)])
def test_update_book_stock_command(system, delta, expected):
    bus, br, or_, ch, qh = system
    ch.handle(create_book_cmd())
    ch.handle(UpdateBookStock(id="b1", quantity=delta))
    assert br.get("b1").stock == expected


def test_create_order_command(system):
    bus, br, or_, ch, qh = system
    br.save(make_book())
    ch.handle(CreateOrder(id="o1", items=[OrderItem(book_id="b1", quantity=3)]))
    assert or_.get("o1").total == 30.0
    assert br.get("b1").stock == 97


# --- Queries --------------------------------------------------------------


def test_query_handler(system):
    bus, br, or_, ch, qh = system
    br.save(make_book())
    assert len(qh.handle(ListBooks())) == 1
    assert qh.handle(GetBook(id="b1")).title == "T"


# --- Events / notifications ----------------------------------------------


def test_stock_alert_notification(system):
    bus, br, or_, ch, qh = system
    nh = NotificationHandler()
    dispatcher = NotificationDispatcher(nh)
    bus.subscribe(BookCreated, dispatcher.on_book_created)
    bus.subscribe(
        StockAlert,
        lambda e: nh.dispatch(
            StockAlert(book_id=e.book_id, current_stock=e.current_stock)
        ),
    )

    alerts = []
    nh.register(StockAlert, lambda n: alerts.append(n.book_id))

    ch.handle(create_book_cmd(stock=3))
    ch.handle(UpdateBookStock(id="b1", quantity=-1))
    assert len(alerts) == 1


if __name__ == "__main__":
    pytest.main()
