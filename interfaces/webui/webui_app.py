from pathlib import Path
import json
import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
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

from cosmo.vision.vision_manager import (
    vision_manager
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
async def dashboard(
    request: Request
):

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "active_page": "dashboard"
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
    search: str | None = None,
    logger_name: str | None = None,
    module: str | None = None,
    function: str | None = None,
):

    try:

        logs = log_repository.get_recent_logs(
            limit=limit,
            level=level,
            search=search,
            logger_name=logger_name,
            module=module,
            function=function
        )

        result = [
            _row_to_dict(log)
            for log in logs
        ]

        return jsonable_encoder(
            result
        )

    except Exception as error:

        return JSONResponse(
            {
                "error": str(
                    error
                )
            },
            status_code=500
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

@app.get("/api/vision/snapshot")
async def api_vision_snapshot():

    snapshot = vision_manager.snapshot()

    snapshot_path = (
        snapshot.get(
            "last_snapshot_path"
        )
        or vision_manager.get_snapshot_path()
    )

    if not snapshot_path:

        return JSONResponse(
            {
                "error": "No vision snapshot path configured"
            },
            status_code=404
        )

    path = Path(
        snapshot_path
    )

    if not path.exists():

        return JSONResponse(
            {
                "error": "Vision snapshot file not found"
            },
            status_code=404
        )

    return FileResponse(
        path,
        media_type="image/jpeg"
    )

@app.get("/")
async def dashboard(
    request: Request
):

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request
        }
    )


@app.get("/vision")
async def vision_page(
    request: Request
):

    return templates.TemplateResponse(
        request,
        "vision.html",
        {
            "request": request,
            "active_page": "vision"
        }
    )


@app.get("/logs")
async def logs_page(
    request: Request
):

    return templates.TemplateResponse(
        request,
        "logs.html",
        {
            "request": request
        }
    )


@app.get("/events")
async def events_page(
    request: Request
):

    return templates.TemplateResponse(
        request,
        "events.html",
        {
            "request": request,
            "active_page": "events"
        }
    )


@app.get("/memory")
async def memory_page(
    request: Request
):

    return templates.TemplateResponse(
        request,
        "memory.html",
        {
            "request": request,
            "active_page": "memory"
        }
    )


@app.get("/conversations")
async def conversations_page(
    request: Request
):

    return templates.TemplateResponse(
        request,
        "conversations.html",
        {
            "request": request,
            "active_page": "conversations"
        }
    )


@app.get("/status")
async def status_page(
    request: Request
):

    return templates.TemplateResponse(
        request,
        "status.html",
        {
            "request": request,
            "active_page": "status"
        }
    )

@app.get("/logs")
async def logs_page(
    request: Request
):

    return templates.TemplateResponse(
        request,
        "logs.html",
        {
            "request": request,
            "active_page": "logs"
        }
    )

