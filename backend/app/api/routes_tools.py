"""Tool endpoints: the generic tool runner plus the special D.A.R.E and Images routes."""
import asyncio
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas import (
    DareArtifactsRequest,
    DareRequest,
    ErrorResponse,
    ImageOut,
    ImagePromptsRequest,
    ImagePromptsResponse,
    ImagesRequest,
    ImagesResponse,
    ResultBlockOut,
    StreamBlockEvent,
    StreamDoneEvent,
    StreamErrorEvent,
    TextResponse,
    ToolRequest,
    ToolResponse,
)
from app.config import get_settings
from app.core.client import get_client
from app.core.errors import PlaygroundError, ValidationError
from app.core.generation import generate_text_async
from app.core.tools import get_tool
from app.core.tools.dare import dare_artifacts, dare_it
from app.core.tools.images import generate_image_prompts, generate_images
from app.core.tools.types import BlockJob, ToolContext
from app.deps import build_context

router = APIRouter()

_ERROR_RESPONSES = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    502: {"model": ErrorResponse},
}


@router.post("/tools/{tool_id}", response_model=ToolResponse, responses=_ERROR_RESPONSES)
def run_tool(tool_id: str, req: ToolRequest) -> ToolResponse:
    spec = get_tool(tool_id)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_id}")
    if not req.input.strip():
        raise ValidationError("Please enter a prompt.")

    ctx = build_context(req.cfg, input=req.input, fields=req.fields)
    result = spec.handler(ctx)
    return ToolResponse(
        tool_id=tool_id,
        blocks=[
            ResultBlockOut(content=b.content, title=b.title, language=b.language)
            for b in result.blocks
        ],
        meta=result.meta,
    )


async def _run_job(
    index: int, job: BlockJob, ctx: ToolContext
) -> StreamBlockEvent | StreamErrorEvent:
    """Run one generation on the async client; never raises.

    Concurrency here goes through ``client.aio`` (one event loop), which is safe
    to drive in parallel — sharing the sync client across threads is not.
    """
    try:
        content = await generate_text_async(
            ctx.client,
            project_id=ctx.project_id,
            region=ctx.region,
            params=ctx.params,
            contents=job.contents,
            system_instruction=job.system_instruction,
        )
        return StreamBlockEvent(index=index, title=job.title, content=content, language=job.language)
    except PlaygroundError as exc:
        return StreamErrorEvent(index=index, title=job.title, error=str(exc), code=exc.code)
    except Exception as exc:  # noqa: BLE001 - one block's failure must not kill the others
        return StreamErrorEvent(index=index, title=job.title, error=str(exc), code="error")


@router.post("/tools/{tool_id}/stream", responses=_ERROR_RESPONSES)
async def run_tool_stream(tool_id: str, req: ToolRequest) -> StreamingResponse:
    """Stream a tool's result blocks as NDJSON, one line per block as it lands.

    Each line is one of :class:`StreamBlockEvent`, :class:`StreamErrorEvent`, or
    (last line) :class:`StreamDoneEvent`, JSON-encoded. Tools that declare
    ``jobs`` (currently Fine-Tune) run them concurrently; others fall back to
    running the sync handler.
    """
    spec = get_tool(tool_id)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_id}")
    if not req.input.strip():
        raise ValidationError("Please enter a prompt.")

    async def emit() -> AsyncIterator[str]:
        if spec.jobs is not None:
            # Built on the event-loop thread: jobs run via `client.aio`, which
            # multiplexes safely within one loop (see client.py).
            ctx = build_context(req.cfg, input=req.input, fields=req.fields)
            tasks = [
                asyncio.create_task(_run_job(i, job, ctx))
                for i, job in enumerate(spec.jobs(ctx))
            ]
            for completed in asyncio.as_completed(tasks):
                yield (await completed).model_dump_json() + "\n"
        else:
            # No explicit jobs: run the sync handler off-thread. The context
            # (and its client) must be built *inside* that worker thread —
            # get_client() is thread-local, so building it here on the event
            # loop thread and handing it to a different worker thread would
            # share one client across threads, which races (see client.py).
            def _run_handler():
                thread_ctx = build_context(req.cfg, input=req.input, fields=req.fields)
                return spec.handler(thread_ctx)

            try:
                result = await asyncio.to_thread(_run_handler)
            except PlaygroundError as exc:
                yield StreamErrorEvent(index=0, error=str(exc), code=exc.code).model_dump_json() + "\n"
            else:
                for i, b in enumerate(result.blocks):
                    yield StreamBlockEvent(
                        index=i, title=b.title, content=b.content, language=b.language
                    ).model_dump_json() + "\n"
        yield StreamDoneEvent().model_dump_json() + "\n"

    return StreamingResponse(
        emit(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/dare", response_model=TextResponse, responses=_ERROR_RESPONSES)
def run_dare(req: DareRequest) -> TextResponse:
    if not req.prompt.strip():
        raise ValidationError("Please enter a prompt.")
    ctx = build_context(req.cfg)
    content = dare_it(
        ctx,
        vision=req.vision,
        mission=req.mission,
        context=req.context,
        prompt=req.prompt,
    )
    return TextResponse(content=content)


@router.post("/dare/artifacts", response_model=TextResponse, responses=_ERROR_RESPONSES)
def run_dare_artifacts(req: DareArtifactsRequest) -> TextResponse:
    if not req.input.strip():
        raise ValidationError("Please enter a prompt.")
    ctx = build_context(req.cfg)
    return TextResponse(content=dare_artifacts(ctx, user_input=req.input))


@router.post("/images/prompts", response_model=ImagePromptsResponse, responses=_ERROR_RESPONSES)
def run_image_prompts(req: ImagePromptsRequest) -> ImagePromptsResponse:
    if not req.description.strip():
        raise ValidationError("Please enter a description.")
    ctx = build_context(req.cfg, input=req.description)
    return ImagePromptsResponse(prompts=generate_image_prompts(ctx, count=req.count))


@router.post("/images/generate", response_model=ImagesResponse, responses=_ERROR_RESPONSES)
def run_image_generate(req: ImagesRequest) -> ImagesResponse:
    if not req.description.strip():
        raise ValidationError("Please enter a description.")
    # Image generation uses Imagen directly; only the client/project are needed.
    s = get_settings()
    client = get_client(s.gcp_project_id, s.gcp_region)
    images = generate_images(client, description=req.description, count=req.count)
    return ImagesResponse(
        images=[ImageOut(mime_type=i.mime_type, data_b64=i.data_b64) for i in images]
    )
