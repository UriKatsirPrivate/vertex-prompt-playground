"""Config endpoint — drives the frontend nav, forms, and slider defaults."""
from fastapi import APIRouter

from app.api.schemas import ConfigDefaults, ConfigResponse, ToolMeta
from app.config import get_settings
from app.core.tools import EXTRA_NAV, TOOL_REGISTRY

router = APIRouter()


@router.get("/config", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    s = get_settings()

    tools = [
        ToolMeta(
            id=spec.id,
            label=spec.label,
            category=spec.category,
            route=f"/{spec.id}",
            placeholder=spec.placeholder,
            help_url=spec.help_url,
            output_kind=spec.output_kind,
            multi_result=spec.multi_result,
            result_count=spec.result_count,
        )
        for spec in TOOL_REGISTRY.values()
    ]
    tools.extend(
        ToolMeta(
            id=extra["id"],
            label=extra["label"],
            category=extra["category"],
            route=extra["route"],
            output_kind="special",
        )
        for extra in EXTRA_NAV
    )

    return ConfigResponse(
        models=s.model_names,
        default_model=s.default_model,
        regions=[s.gcp_region],
        defaults=ConfigDefaults(
            temperature=s.default_temperature,
            top_p=s.default_top_p,
            max_tokens=s.default_max_tokens,
            temperature_range=[0.0, 2.0],
            top_p_range=[0.0, 1.0],
            max_tokens_range=[1, s.max_tokens_limit],
        ),
        tools=tools,
    )
