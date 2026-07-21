"""Application settings, sourced from environment variables (prefix ``PG_``).

Replaces the Streamlit ``st.secrets`` / ``get_project_id()`` lookup. On Cloud Run
the runtime service account supplies ADC, so no API key is needed — only the
project id and (optionally) model defaults.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PG_", env_file=".env", extra="ignore")

    # Vertex / GCP
    gcp_project_id: str = "landing-zone-demo-341118"
    gcp_region: str = "global"

    # Models
    model_names: list[str] = [
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
        "gemini-3.1-pro-preview",
    ]
    default_model: str = "gemini-3.5-flash-lite"
    imagen_model: str = "imagen-4.0-fast-generate-001"

    # Generation defaults (mirror the old Streamlit sliders)
    default_temperature: float = 1.0
    default_top_p: float = 0.8
    default_max_tokens: int = 65535
    max_tokens_limit: int = 65535

    # CORS (dev only — in the single-container prod build the SPA is same-origin)
    cors_origins: list[str] = ["http://localhost:3000"]

    # Path to the built Next.js static export, mounted at "/" in prod.
    static_dir: str = "static"


@lru_cache
def get_settings() -> Settings:
    return Settings()
