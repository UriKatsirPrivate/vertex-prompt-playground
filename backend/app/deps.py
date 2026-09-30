"""FastAPI dependency providers."""
from app.api.schemas import ModelConfig
from app.config import Settings, get_settings
from app.core.client import get_client
from app.core.generation import GenerationParams
from app.core.tools.types import ToolContext


def build_context(model_config: ModelConfig, *, input: str = "", fields: dict | None = None) -> ToolContext:
    settings: Settings = get_settings()
    client = get_client(settings.gcp_project_id, settings.gcp_region)
    params = GenerationParams(
        model_name=model_config.model_name,
        max_tokens=model_config.max_tokens,
    )
    return ToolContext(
        client=client,
        project_id=settings.gcp_project_id,
        region=settings.gcp_region,
        params=params,
        input=input,
        fields=fields or {},
    )
