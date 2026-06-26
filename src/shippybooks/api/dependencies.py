from typing import Annotated

from fastapi import Depends, Request

from ..events import NotificationStore
from ..services import CommandHandler, QueryHandler


def get_cmd_handler(request: Request) -> CommandHandler:
    return request.app.state.cmd_handler


def get_query_handler(request: Request) -> QueryHandler:
    return request.app.state.query_handler


def get_notification_store(request: Request) -> NotificationStore:
    return request.app.state.notification_store


CmdHandlerDep = Annotated[CommandHandler, Depends(get_cmd_handler)]
QueryHandlerDep = Annotated[QueryHandler, Depends(get_query_handler)]
NotificationStoreDep = Annotated[
    NotificationStore, Depends(get_notification_store)
]
