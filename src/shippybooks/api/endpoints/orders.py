"""API endpoints for managing orders."""

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...domain import (
    ChangeOrderStatus,
    CreateOrder,
    GetOrder,
    ListOrders,
    Order,
    OrderItem,
    OrderStatus,
)
from ..dependencies import CmdHandlerDep, QueryHandlerDep

router = APIRouter()


class CreateOrderRequest(BaseModel):
    """Request model for creating an order."""

    items: list[OrderItem] = Field(default_factory=list)


class ChangeStatusRequest(BaseModel):
    """Request model for changing order status."""

    status: str


@router.post("/orders/")
def create_order(
    request: CreateOrderRequest,
    cmd_handler: CmdHandlerDep,
) -> dict[str, str]:
    """Create a new order."""
    cmd = CreateOrder(id=str(uuid.uuid4()), items=request.items)
    cmd_handler.handle(cmd)
    return {"status": "created", "id": cmd.id}


@router.post("/orders/{order_id}/status/")
def change_status(
    order_id: str,
    request: ChangeStatusRequest,
    cmd_handler: CmdHandlerDep,
) -> dict[str, str]:
    """Change the status of an existing order."""
    try:
        cmd_handler.handle(
            ChangeOrderStatus(id=order_id, new_status=OrderStatus(request.status))
        )
    except ValueError as e:
        raise HTTPException(400, "Invalid status:" + str(e)) from e
    return {"status": "updated"}


@router.get("/orders/{order_id}")
def get_order(order_id: str, query_handler: QueryHandlerDep) -> Order:
    """Retrieve an order by its ID."""
    try:
        order: Order = query_handler.handle(GetOrder(id=order_id))
    except KeyError as e:
        raise HTTPException(404, "Not found" + str(e)) from e
    return order


@router.get("/orders/")
def list_orders(query_handler: QueryHandlerDep) -> list[dict[str, str]]:
    """List all orders."""
    return [
        {"id": o.id, "status": o.status.value}
        for o in query_handler.handle(ListOrders())
    ]
