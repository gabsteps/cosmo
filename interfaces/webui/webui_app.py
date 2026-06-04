from pathlib import Path
import json
import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles

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

from cosmo.cognition.memory.memory_manager import (
    memory_manager
)


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="Zenith Cosmo WebUI"
)

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static"
)

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


@app.get("/api/status/stream")
async def api_status_stream():

    async def event_generator():

        while True:

            snapshot = diagnostics_manager.compact_snapshot()

            payload = json.dumps(
                snapshot,
                ensure_ascii=False,
                default=str
            )

            yield f"data: {payload}\n\n"

            await asyncio.sleep(
                1
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.get("/api/memories")
async def api_memories(
    limit: int = 50,
    category: str | None = None,
    search: str | None = None
):

    memories = memory_repository.get_recent_memories(
        user_id=memory_manager.default_user_id,
        limit=limit
    )

    result = [
        _row_to_dict(memory)
        for memory in memories
    ]

    if category:

        result = [
            memory
            for memory in result
            if memory.get("category") == category
        ]

    if search:

        normalized_search = search.lower()

        result = [
            memory
            for memory in result
            if normalized_search in str(
                memory.get(
                    "content",
                    ""
                )
            ).lower()
        ]

    return jsonable_encoder(
        result
    )


@app.get("/api/conversations")
async def api_conversations(
    limit: int = 50,
    role: str | None = None,
    search: str | None = None
):

    conversations = (
        conversation_repository
        .get_recent_conversation_context(
            user_id=memory_manager.default_user_id,
            limit=limit
        )
    )

    result = [
        _row_to_dict(message)
        for message in conversations
    ]

    if role:

        result = [
            message
            for message in result
            if message.get("role") == role
        ]

    if search:

        normalized_search = search.lower()

        result = [
            message
            for message in result
            if normalized_search in str(
                message.get(
                    "message",
                    ""
                )
            ).lower()
        ]

    return jsonable_encoder(
        result
    )


@app.get("/api/events")
async def api_events(
    limit: int = 50,
    event_type: str | None = None,
    search: str | None = None
):

    events = event_repository.get_recent_events(
        limit=limit,
        event_type=event_type
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

    if search:

        normalized_search = search.lower()

        result = [
            event
            for event in result
            if (
                normalized_search in str(
                    event.get(
                        "type",
                        ""
                    )
                ).lower()
                or normalized_search in str(
                    event.get(
                        "payload",
                        ""
                    )
                ).lower()
            )
        ]

    return jsonable_encoder(
        result
    )


@app.get("/api/logs")
async def api_logs(
    limit: int = 200,
    level: str | None = None,
    search: str | None = None
):

    logs = log_repository.get_recent_logs(
        limit=limit,
        level=level
    )

    result = [
        _row_to_dict(log)
        for log in logs
    ]

    if search:

        normalized_search = search.lower()

        result = [
            log
            for log in result
            if (
                normalized_search in str(
                    log.get(
                        "message",
                        ""
                    )
                ).lower()
                or normalized_search in str(
                    log.get(
                        "module",
                        ""
                    )
                ).lower()
                or normalized_search in str(
                    log.get(
                        "function",
                        ""
                    )
                ).lower()
                or normalized_search in str(
                    log.get(
                        "level",
                        ""
                    )
                ).lower()
            )
        ]

    return jsonable_encoder(
        result
    )


def _row_to_dict(
    row
) -> dict:

    return dict(
        row
    )


def _decode_event_payload(
    payload
):

    if payload is None:
        return None

    try:

        return json.loads(
            payload
        )

    except Exception:

        return payload