from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..domain import Book, Order, OrderItem, OrderStatus
from . import Base


class BookORM(Base):
    """Book ORM model."""

    __tablename__ = "books"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    price = Column(Float)
    stock = Column(Integer)

    def to_domain(self) -> Book:
        """Convert ORM model to domain model."""
        return Book(
            id=self.id,
            title=self.title,
            author=self.author,
            price=self.price,
            stock=self.stock,
        )


class OrderItemORM(Base):
    """Order item ORM model."""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"))
    book_id = Column(String, ForeignKey("books.id"))
    quantity = Column(Integer)

    def to_domain(self) -> OrderItem:
        """Convert ORM model to domain model."""
        return OrderItem(
            book_id=self.book_id,
            quantity=self.quantity,
        )


class OrderORM(Base):
    """Order ORM model."""

    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default=OrderStatus.PENDING.value)
    total = Column(Float, default=0.0)

    items = relationship("OrderItemORM", backref="order", cascade="all, delete-orphan")

    def to_domain(self) -> Order:
        """Convert ORM model to domain model."""
        return Order(
            id=self.id,
            items=[item.to_domain() for item in self.items],
            timestamp=self.timestamp,
            last_updated=self.last_updated,
            status=OrderStatus(self.status),
            total=self.total,
        )
