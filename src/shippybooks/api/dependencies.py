from typing import Annotated

from fastapi import Depends, Request

from ..services import CommandHandler, QueryHandler


def get_cmd_handler(request: Request) -> CommandHandler:
    """Retrieve command handler from app state."""
    return request.app.state.cmd_handler


def get_query_handler(request: Request) -> QueryHandler:
    """Retrieve query handler from app state."""
    return request.app.state.query_handler


CmdHandlerDep = Annotated[CommandHandler, Depends(get_cmd_handler)]
QueryHandlerDep = Annotated[QueryHandler, Depends(get_query_handler)]
