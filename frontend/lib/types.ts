// TypeScript mirrors of the FastAPI schemas (see backend/app/api/schemas.py).

export interface ModelConfig {
  model_name: string;
  temperature: number;
  top_p: number;
  max_tokens: number;
}

export interface ResultBlock {
  content: string;
  title?: string | null;
  language?: string | null;
}

export interface ToolResponse {
  tool_id: string;
  blocks: ResultBlock[];
  meta: Record<string, unknown>;
}

export interface ToolMeta {
  id: string;
  label: string;
  category: string;
  route: string;
  placeholder: string;
  help_url?: string | null;
  output_kind: string; // "text" | "json" | "stats" | "special"
  multi_result: boolean;
  result_count: number;
}

export interface ConfigDefaults {
  temperature: number;
  top_p: number;
  max_tokens: number;
  temperature_range: [number, number];
  top_p_range: [number, number];
  max_tokens_range: [number, number];
}

export interface AppConfig {
  models: string[];
  default_model: string;
  regions: string[];
  defaults: ConfigDefaults;
  tools: ToolMeta[];
}

export interface ImageOut {
  mime_type: string;
  data_b64: string;
}

export interface ApiErrorBody {
  detail: string;
  code: string;
}
