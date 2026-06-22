from dataclasses import dataclass


@dataclass
class Query:
    pass


@dataclass
class GetBook(Query):
    id: str


@dataclass
class ListBooks(Query):
    pass


@dataclass
class GetOrder(Query):
    id: str


@dataclass
class ListOrders(Query):
    pass
