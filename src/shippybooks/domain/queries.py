from pydantic import BaseModel, ConfigDict


class Query(BaseModel):
    model_config = ConfigDict(frozen=True)


class GetBook(Query):
    id: str


class ListBooks(Query):
    pass


class GetOrder(Query):
    id: str


class ListOrders(Query):
    pass
