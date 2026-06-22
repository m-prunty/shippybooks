import uuid

from fastapi import APIRouter, HTTPException

from ...domain import CreateBook, GetBook, ListBooks, UpdateBookStock
from ..dependencies import CmdHandlerDep, QueryHandlerDep

router = APIRouter()


@router.post("/books/")
def create_book(
    title: str,
    author: str,
    price: float,
    stock: int,
    cmd_handler: CmdHandlerDep,
) -> dict:
    cmd = CreateBook(
        id=str(uuid.uuid4()),
        title=title,
        author=author,
        price=price,
        stock=stock,
    )
    cmd_handler.handle(cmd)
    return {"status": "created", "id": cmd.id}


@router.post("/books/{book_id}/stock/")
def update_stock(book_id: str, quantity: int, cmd_handler: CmdHandlerDep):
    cmd_handler.handle(UpdateBookStock(id=book_id, quantity=quantity))
    return {"status": "updated"}


@router.get("/books/{book_id}")
def get_book(book_id: str, query_handler: QueryHandlerDep):
    try:
        book: QueryHandler = query_handler.handle(GetBook(id=book_id))
    except KeyError:
        raise HTTPException(404, "Not found")
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "price": book.price,
        "stock": book.stock,
    }


@router.get("/books/")
def list_books(query_handler: QueryHandlerDep):
    return [
        {"id": b.id, "title": b.title, "stock": b.stock}
        for b in query_handler.handle(ListBooks())
    ]
