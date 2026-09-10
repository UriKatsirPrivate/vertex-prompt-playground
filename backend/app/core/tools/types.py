"""Shared types for the tool registry."""
from dataclasses import dataclass, field
from typing import Callable

from google import genai

from app.core.generation import GenerationParams


@dataclass
class ToolContext:
    """Everything a tool handler needs for one invocation."""

    client: genai.Client
    project_id: str
    region: str
    params: GenerationParams
    input: str = ""
    fields: dict[str, str] = field(default_factory=dict)


@dataclass
class ResultBlock:
    content: str
    title: str | None = None
    language: str | None = None  # e.g. "json" → frontend syntax highlighting


@dataclass
class ToolResult:
    blocks: list[ResultBlock]
    meta: dict = field(default_factory=dict)


@dataclass
class BlockJob:
    """One streamable unit of work: a single generation that becomes a block.

    A tool that exposes ``jobs`` lets the streaming endpoint run each job
    concurrently (via the async client) and push its block the moment it
    finishes, instead of waiting for the whole :class:`ToolResult`. The job is
    plain data (the prompt) rather than a bound call, so the same jobs can be
    driven by either the sync handler or the async streaming path.
    """

    title: str | None
    contents: str
    system_instruction: str | None = None
    language: str | None = None


Handler = Callable[[ToolContext], ToolResult]
JobsBuilder = Callable[[ToolContext], list[BlockJob]]


@dataclass
class ToolSpec:
    id: str
    label: str
    category: str
    handler: Handler
    placeholder: str = ""
    help_url: str | None = None
    output_kind: str = "text"  # "text" | "json" | "toon" | "stats"
    multi_result: bool = False
    # Number of result blocks the frontend should render slots for (streaming
    # and loading-skeleton layouts key off this instead of assuming 4).
    result_count: int = 1
    # Optional: per-block jobs for the streaming endpoint. When set, the same
    # jobs back both the sync handler and ``/api/tools/{id}/stream``.
    jobs: JobsBuilder | None = None
