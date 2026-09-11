// Generic tool ids served by the [toolId] route. Static export must enumerate
// dynamic params at build time (generateStaticParams), so this list mirrors the
// backend's TOOL_REGISTRY (backend/app/core/tools/__init__.py). The two special
// tools (dare, images) have their own dedicated routes and are NOT listed here.
//
// Adding a backend tool: add its id here and rebuild. The nav (from /api/config)
// shows new tools automatically, but a static per-tool route needs this entry.
export const GENERIC_TOOL_IDS = [
  "fine_tune",
  "system_prompt",
  "agent_prompt",
  "meta_prompt",
  "zero_to_few",
  "chain_of_thought",
  "json_prompt",
  "nano_banana",
  "veo_prompt",
  "run_prompt",
  "compress",
] as const;

export const CATEGORY_ORDER = [
  "Generate",
  "Transform",
  "Media",
  "Run",
  "Utilities",
];
