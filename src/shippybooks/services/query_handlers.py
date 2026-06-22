from typing import Any

from domain.queries import GetBook, GetOrder, ListBooks, ListOrders, Query

from .command_handlers import BookRepository, OrderRepository


class QueryHandler:
    def __init__(
        self, book_repo: BookRepository, order_repo: OrderRepository
    ) -> None:
        self.book_repo = book_repo
        self.order_repo = order_repo

    def handle(self, query: Query) -> Any:
        if isinstance(query, GetBook):
            return self.book_repo.get(query.id)
        if isinstance(query, ListBooks):
            return self.book_repo.all()
        if isinstance(query, GetOrder):
            return self.order_repo.get(query.id)
        if isinstance(query, ListOrders):
            return self.order_repo.all()
