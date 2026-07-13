import uuid

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from ...domain import Book, CreateBook, GetBook, ListBooks, UpdateBookStock
from ..dependencies import CmdHandlerDep, QueryHandlerDep

router = APIRouter()


class CreateBookRequest(BaseModel):
    """Request model for creating a book."""

    title: str
    author: str
    price: float
    stock: int


class UpdateStockRequest(BaseModel):
    """Request model for updating book stock."""

    book_id: str
    quantity: int


@router.post("/books/")
def create_book(
    request: CreateBookRequest,
    cmd_handler: CmdHandlerDep,
) -> dict[str, str]:
    """Create a new book."""
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
    """Update the stock of an existing book."""
    cmd_handler.handle(UpdateBookStock(id=book_id, quantity=quantity))
    return {"status": "updated"}


@router.get("/books/{book_id}", response_model=Book)
def get_book(book_id: str, query_handler: QueryHandlerDep) -> Book:
    """Retrieve a book by its ID."""
    try:
        book: Book = query_handler.handle(GetBook(id=book_id))
    except KeyError as e:
        raise HTTPException(404, "Not found: " + str(e)) from e
    return book


@router.get("/books/")
def list_books(query_handler: QueryHandlerDep) -> list[dict[str, str | int]]:
    """List all books in the repository."""
    return [
        {"id": b.id, "title": b.title, "stock": b.stock}
        for b in query_handler.handle(ListBooks())
    ]
