"""Pydantic request/response models for the API."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import get_settings

# Requests carry the model config under the JSON key "modelConfig". We expose it
# on a Python attribute named ``cfg`` (avoiding Pydantic's protected ``model_``
# namespace) and accept the field by either name.
_REQUEST_CONFIG = ConfigDict(populate_by_name=True)


class ModelConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    top_p: float = Field(default=0.8, ge=0.0, le=1.0)
    max_tokens: int = Field(default=65535, ge=1)

    @field_validator("model_name")
    @classmethod
    def _model_name_allowed(cls, v: str) -> str:
        allowed = get_settings().model_names
        if v not in allowed:
            raise ValueError(f"Unknown model: {v!r}. Must be one of {allowed}.")
        return v

    @field_validator("max_tokens")
    @classmethod
    def _max_tokens_within_limit(cls, v: int) -> int:
        limit = get_settings().max_tokens_limit
        if v > limit:
            raise ValueError(f"max_tokens must be <= {limit}.")
        return v


def default_model_config() -> ModelConfig:
    s = get_settings()
    return ModelConfig(
        model_name=s.default_model,
        temperature=s.default_temperature,
        top_p=s.default_top_p,
        max_tokens=s.default_max_tokens,
    )


# ---- Generic tool endpoint ----
class ToolRequest(BaseModel):
    model_config = _REQUEST_CONFIG

    input: str = ""
    cfg: Annotated[ModelConfig, Field(alias="modelConfig")]
    fields: dict[str, str] = {}


class ResultBlockOut(BaseModel):
    content: str
    title: str | None = None
    language: str | None = None


class ToolResponse(BaseModel):
    tool_id: str
    blocks: list[ResultBlockOut]
    meta: dict = {}


# ---- D.A.R.E ----
class DareRequest(BaseModel):
    model_config = _REQUEST_CONFIG

    vision: str = ""
    mission: str = ""
    context: str = ""
    prompt: str
    cfg: Annotated[ModelConfig, Field(alias="modelConfig")]


class DareArtifactsRequest(BaseModel):
    model_config = _REQUEST_CONFIG

    input: str
    cfg: Annotated[ModelConfig, Field(alias="modelConfig")]


class TextResponse(BaseModel):
    content: str


# ---- Images ----
class ImagePromptsRequest(BaseModel):
    model_config = _REQUEST_CONFIG

    description: str
    count: int = Field(default=2, ge=1, le=8)
    cfg: Annotated[ModelConfig, Field(alias="modelConfig")]


class ImagePromptsResponse(BaseModel):
    prompts: str


class ImagesRequest(BaseModel):
    description: str
    count: int = Field(default=2, ge=1, le=8)


class ImageOut(BaseModel):
    mime_type: str
    data_b64: str


class ImagesResponse(BaseModel):
    images: list[ImageOut]


# ---- Config ----
class ToolMeta(BaseModel):
    id: str
    label: str
    category: str
    route: str
    placeholder: str = ""
    help_url: str | None = None
    output_kind: str = "text"
    multi_result: bool = False
    result_count: int = 1


class ConfigDefaults(BaseModel):
    temperature: float
    top_p: float
    max_tokens: int
    temperature_range: list[float]
    top_p_range: list[float]
    max_tokens_range: list[int]


class ConfigResponse(BaseModel):
    models: list[str]
    default_model: str
    regions: list[str]
    defaults: ConfigDefaults
    tools: list[ToolMeta]


class ErrorResponse(BaseModel):
    detail: str
    code: str


# ---- NDJSON stream wire format for /api/tools/{tool_id}/stream ----
class StreamBlockEvent(BaseModel):
    index: int
    title: str | None = None
    content: str
    language: str | None = None


class StreamErrorEvent(BaseModel):
    index: int
    title: str | None = None
    error: str
    code: str


class StreamDoneEvent(BaseModel):
    done: bool = True
