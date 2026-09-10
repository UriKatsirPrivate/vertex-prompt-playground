"""Tool registry.

Maps a ``tool_id`` to a :class:`ToolSpec` so a single generic endpoint serves
every text/JSON tool. The two special tools (D.A.R.E, Images) have their own
endpoints and are not registered here, but appear in nav via ``EXTRA_NAV``.

``category`` drives the grouped sidebar in the frontend.
"""
from app.core.tools import json_tools, text_tools
from app.core.tools.compress import compress
from app.core.tools.types import ToolSpec

TOOL_REGISTRY: dict[str, ToolSpec] = {
    spec.id: spec
    for spec in [
        # --- Generate ---
        ToolSpec(
            id="fine_tune",
            label="Fine-Tune Prompt",
            category="Generate",
            handler=text_tools.fine_tune,
            placeholder="tweet about Israel",
            multi_result=True,
            result_count=4,
            jobs=text_tools.fine_tune_jobs,
        ),
        ToolSpec(
            id="system_prompt",
            label="System Prompt",
            category="Generate",
            handler=text_tools.system_prompt,
        ),
        ToolSpec(
            id="agent_prompt",
            label="Agent Prompt",
            category="Generate",
            handler=text_tools.agent,
        ),
        ToolSpec(
            id="meta_prompt",
            label="Meta Prompt",
            category="Generate",
            handler=text_tools.meta,
            help_url="https://meta-prompting.github.io/",
        ),
        # --- Transform ---
        ToolSpec(
            id="zero_to_few",
            label="Zero to Few",
            category="Transform",
            handler=text_tools.zero_to_few,
            help_url="https://www.promptingguide.ai/techniques/fewshot",
        ),
        ToolSpec(
            id="chain_of_thought",
            label="Chain of Thought",
            category="Transform",
            handler=text_tools.chain_of_thought,
            help_url="https://www.promptingguide.ai/techniques/cot",
        ),
        ToolSpec(
            id="json_prompt",
            label="Json Prompt",
            category="Transform",
            handler=json_tools.json_prompt,
            output_kind="json",
        ),
        ToolSpec(
            id="toon_prompt",
            label="Toon Prompt",
            category="Transform",
            handler=json_tools.toon_prompt,
            help_url="https://github.com/xaviviro/python-toon",
            output_kind="toon",
        ),
        # --- Media ---
        ToolSpec(
            id="nano_banana",
            label="Nano Banana Json Prompt",
            category="Media",
            handler=text_tools.nano_banana,
            output_kind="json",
        ),
        ToolSpec(
            id="veo_prompt",
            label="Veo Prompt",
            category="Media",
            handler=text_tools.veo,
        ),
        # --- Run / Utilities ---
        ToolSpec(
            id="run_prompt",
            label="Run Prompt",
            category="Run",
            handler=text_tools.run,
        ),
        ToolSpec(
            id="compress",
            label="Compress Prompt",
            category="Utilities",
            handler=compress,
            output_kind="stats",
        ),
    ]
}

# Special tools that have dedicated endpoints/pages but still need a nav entry.
EXTRA_NAV = [
    {"id": "dare", "label": "D.A.R.E Prompting", "category": "Generate", "route": "/dare"},
    {"id": "images", "label": "Images", "category": "Media", "route": "/images"},
]


def get_tool(tool_id: str) -> ToolSpec | None:
    return TOOL_REGISTRY.get(tool_id)
