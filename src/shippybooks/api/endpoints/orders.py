from fastapi import APIRouter, HTTPException

from ...domain import ChangeOrderStatus, CreateOrder, GetOrder, ListOrders
from ..dependencies import CmdHandlerDep, QueryHandlerDep

router = APIRouter()


@router.post("/orders/")
def create_order(items: list[tuple[str, int]], cmd_handler: CmdHandlerDep):
    cmd = CreateOrder(id=str(uuid.uuid4()), items=items)
    cmd_handler.handle(cmd)
    return {"status": "created", "id": cmd.id}


@router.post("/orders/{order_id}/status/")
def change_status(order_id: str, status: str, cmd_handler: CmdHandlerDep):
    try:
        cmd_handler.handle(
            ChangeOrderStatus(id=order_id, new_status=OrderStatus(status))
        )
    except ValueError:
        raise HTTPException(400, "Invalid status")
    return {"status": "updated"}


@router.get("/orders/{order_id}")
def get_order(order_id: str, query_handler: QueryHandlerDep):
    try:
        order = query_handler.handle(GetOrder(id=order_id))
    except KeyError:
        raise HTTPException(404, "Not found")
    return {"id": order.id, "status": order.status.value, "total": order.total}


@router.get("/orders/")
def list_orders(query_handler: QueryHandlerDep):
    return [
        {"id": o.id, "status": o.status.value}
        for o in query_handler.handle(ListOrders())
    ]
