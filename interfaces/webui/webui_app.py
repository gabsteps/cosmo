from pathlib import Path
import json
import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

from cosmo.data.diagnostics.diagnostics_manager import (
    diagnostics_manager
)
from cosmo.data.database.repositories.memory_repository import (
    memory_repository
)
from cosmo.data.database.repositories.conversation_repository import (
    conversation_repository
)
from cosmo.data.database.repositories.event_repository import (
    event_repository
)
from cosmo.data.database.repositories.log_repository import (
    log_repository
)


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI()
templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


@app.get("/")
async def index(
    request: Request
):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request
        }
    )


@app.get("/api/status/compact")
async def api_status_compact():
    return JSONResponse(
        diagnostics_manager.compact_snapshot()
    )


@app.get("/api/memories")
async def api_memories():
    return JSONResponse(
        memory_repository.get_recent_memories(
            user_id=1,
            limit=50
        )
    )


@app.get("/api/conversations")
async def api_conversations():
    return JSONResponse(
        conversation_repository.get_recent_conversation_context(
            user_id=1,
            limit=50
        )
    )


@app.get("/api/events")
async def api_events(
    limit: int = 50
):

    events = event_repository.get_recent_events(
        limit=limit
    )

    result = []

    for event in events:

        event_data = _row_to_dict(
            event
        )

        event_data["payload"] = _decode_event_payload(
            event_data.get("payload")
        )

        result.append(
            event_data
        )

    return jsonable_encoder(
        result
    )


@app.get("/api/logs")
async def api_logs(
    limit: int = 200,
    level: str | None = None
):

    logs = log_repository.get_recent_logs(
        limit=limit,
        level=level
    )

    result = [
        _row_to_dict(log)
        for log in logs
    ]

    return jsonable_encoder(
        result
    )

@app.get("/api/status/stream")
async def api_status_stream():

    async def event_generator():

        last_heartbeat_count = None

        while True:

            snapshot = diagnostics_manager.compact_snapshot()

            payload = json.dumps(
                snapshot,
                ensure_ascii=False,
                default=str
            )

            yield (
                f"data: {payload}\n\n"
            )

            heartbeat_count = snapshot.get(
                "heartbeat_count"
            )

            if heartbeat_count != last_heartbeat_count:
                last_heartbeat_count = heartbeat_count

            await asyncio.sleep(
                1
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
def _row_to_dict(row):

    return dict(row)


def _decode_event_payload(payload):

    if payload is None:
        return None

    try:
        return json.loads(payload)

    except Exception:
        return payload