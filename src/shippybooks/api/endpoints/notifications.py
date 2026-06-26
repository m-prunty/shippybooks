import asyncio
import json
from typing import Annotated

from fastapi import APIRouter, Header, Request
from fastapi.responses import StreamingResponse

from ..dependencies import NotificationStoreDep

router = APIRouter()


@router.get("/notifications/stream")
async def notification_stream(
    request: Request,
    store: NotificationStoreDep,
    last_event_id: Annotated[str | None, Header(alias="last-event-id")] = None,
) -> StreamingResponse:
    last_seen = int(last_event_id) if last_event_id is not None else -1

    async def generate():
        nonlocal last_seen
        while not await request.is_disconnected():
            for event in store.since(last_seen):
                last_seen = event["id"]
                yield f"id: {event['id']}\ndata: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Critical — prevents nginx buffering the stream
        },
    )
