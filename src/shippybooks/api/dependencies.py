from typing import Annotated, cast

from fastapi import Depends, Request

from ..bootstrap import AppState
from ..events import NotificationStore
from ..services import CommandHandler, QueryHandler


def get_app_state(request: Request) -> AppState:
    """Return the typed application state for the current request."""
    return cast(AppState, request.app.state.app_state)


def get_cmd_handler(request: Request) -> CommandHandler:
    """Return the shared command handler."""
    return get_app_state(request).cmd_handler


def get_query_handler(request: Request) -> QueryHandler:
    """Return the shared query handler."""
    return get_app_state(request).query_handler


def get_notification_store(request: Request) -> NotificationStore:
    """Return the shared notification store."""
    return get_app_state(request).notification_store


CmdHandlerDep = Annotated[CommandHandler, Depends(get_cmd_handler)]
QueryHandlerDep = Annotated[QueryHandler, Depends(get_query_handler)]
NotificationStoreDep = Annotated[NotificationStore, Depends(get_notification_store)]
