"""JSON-scored tools: Json Prompt and Toon Prompt.

Both call the JSON prompter, parse the response, and select the highest-``score``
candidate (ported from the parsing logic in ``app.py``). Toon additionally
encodes the winner into TOON format.
"""
import json

from toon import encode

from app.core.generation import generate_text
from app.core.prompts.system_prompts import JSON_PROMPT
from app.core.tools.types import ResultBlock, ToolContext, ToolResult


def _clean_json_string(s: str) -> str:
    """Strip markdown code-fence formatting (mirrors app.py:clean_json_string)."""
    s = s.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    return s.strip().strip("`")


def _best_candidate(raw_text: str):
    """Parse the JSON prompter output and return (best_obj | None, cleaned_text).

    Returns the max-``score`` object with ``score`` removed when the response is a
    scored array; otherwise ``None`` (caller falls back to the cleaned text).
    """
    cleaned = _clean_json_string(raw_text)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return None, cleaned

    if isinstance(parsed, list) and parsed and all(isinstance(r, dict) and "score" in r for r in parsed):
        best = max(parsed, key=lambda x: x.get("score", 0))
        best.pop("score", None)
        return best, cleaned
    return None, cleaned


def _json_prompter_text(ctx: ToolContext) -> str:
    return generate_text(
        ctx.client,
        project_id=ctx.project_id,
        region=ctx.region,
        params=ctx.params,
        contents=JSON_PROMPT.format(user_input=ctx.input),
    )


def json_prompt(ctx: ToolContext) -> ToolResult:
    best, cleaned = _best_candidate(_json_prompter_text(ctx))
    content = json.dumps(best, indent=2) if best is not None else cleaned
    return ToolResult(blocks=[ResultBlock(content=content, language="json")])


def toon_prompt(ctx: ToolContext) -> ToolResult:
    best, cleaned = _best_candidate(_json_prompter_text(ctx))
    if best is not None:
        json_content = json.dumps(best, indent=2)
        toon_content = encode(best)
    else:
        json_content = cleaned
        toon_content = ""
    return ToolResult(
        blocks=[
            ResultBlock(title="JSON Prompt", content=json_content, language="json"),
            ResultBlock(title="TOON", content=toon_content),
        ]
    )
