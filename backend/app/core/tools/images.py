"""Image tools — Imagen prompt generation and image generation.

Ported from ``utils.py:GenerateImagePrompt`` / ``GenerateImageNew``. Image bytes
are returned base64-encoded so the API can hand them to the frontend in JSON
(rendered inline + downloadable), replacing the old ``_pil_image`` Streamlit path.
"""
import base64
import io
from dataclasses import dataclass

from google import genai
from google.genai import types

from app.config import get_settings
from app.core.errors import SafetyBlockedError, UpstreamError
from app.core.generation import generate_text
from app.core.prompts.image_prompts import GenerateImageSystemPrompt
from app.core.tools.types import ToolContext


@dataclass
class GeneratedImageOut:
    mime_type: str
    data_b64: str


def generate_image_prompts(ctx: ToolContext, *, count: int = 2) -> str:
    """Return markdown text containing ``count`` Imagen prompt variations."""
    prompt = f"Please generate {count} prompt(s) about: {ctx.input}"
    return generate_text(
        ctx.client,
        project_id=ctx.project_id,
        region=ctx.region,
        params=ctx.params,
        contents=prompt,
        system_instruction=GenerateImageSystemPrompt,
    )


def _image_bytes(generated_image) -> bytes:
    """Extract JPEG bytes from a genai GeneratedImage, with a PIL fallback."""
    image = generated_image.image
    data = getattr(image, "image_bytes", None)
    if data:
        return data
    pil = getattr(image, "_pil_image", None)
    if pil is not None:
        buf = io.BytesIO()
        pil.save(buf, format="JPEG")
        return buf.getvalue()
    raise UpstreamError("Generated image contained no readable bytes.")


def generate_images(
    client: genai.Client, *, description: str, count: int = 2
) -> list[GeneratedImageOut]:
    settings = get_settings()
    try:
        result = client.models.generate_images(
            prompt=description,
            model=settings.imagen_model,
            config=types.GenerateImagesConfig(
                number_of_images=count,
                output_mime_type="image/jpeg",
                safety_filter_level="BLOCK_ONLY_HIGH",
                person_generation=types.PersonGeneration.ALLOW_ADULT,
                aspect_ratio="9:16",
            ),
        )
    except Exception as e:  # noqa: BLE001
        raise UpstreamError(str(e)) from e

    generated = getattr(result, "generated_images", None) or []
    if not generated:
        raise SafetyBlockedError(
            "No images were generated. The prompt may have been blocked by safety filters."
        )

    out: list[GeneratedImageOut] = []
    for g in generated:
        data = _image_bytes(g)
        out.append(
            GeneratedImageOut(
                mime_type="image/jpeg",
                data_b64=base64.b64encode(data).decode("ascii"),
            )
        )
    return out
