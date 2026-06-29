import uuid

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from ...domain import CreateBook, GetBook, ListBooks, UpdateBookStock
from ..dependencies import CmdHandlerDep, QueryHandlerDep

router = APIRouter()


class CreateBookRequest(BaseModel):
    title: str
    author: str
    price: float
    stock: int


class UpdateStockRequest(BaseModel):
    book_id: str
    quantity: int


@router.post("/books/")
def create_book(
    request: CreateBookRequest,
    cmd_handler: CmdHandlerDep,
) -> dict[str, str]:
    cmd = CreateBook(
        id=str(uuid.uuid4()),
        **request.model_dump(),
    )
    cmd_handler.handle(cmd)
    return {"status": "created", "id": cmd.id}


@router.post("/books/{book_id}/stock/")
def update_stock(
    book_id: str,
    cmd_handler: CmdHandlerDep,
    quantity: int = Body(..., embed=True),
) -> dict[str, str]:
    cmd_handler.handle(UpdateBookStock(id=book_id, quantity=quantity))
    return {"status": "updated"}


@router.get("/books/{book_id}")
def get_book(book_id: str, query_handler: QueryHandlerDep):
    try:
        book: Book = query_handler.handle(GetBook(id=book_id))
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
