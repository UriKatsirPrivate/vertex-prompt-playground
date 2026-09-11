// Typed API client. Base URL is empty in production (same-origin static export);
// in dev set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000.
import type {
  AppConfig,
  ImageOut,
  ModelConfig,
  ToolResponse,
} from "@/lib/types";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(message: string, code: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}/api${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    });
  } catch {
    throw new ApiError("Network error — is the API running?", "network_error", 0);
  }

  if (!res.ok) {
    let code = "error";
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
      code = body.code ?? code;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(detail, code, res.status);
  }
  return res.json() as Promise<T>;
}

export function getConfig(): Promise<AppConfig> {
  return request<AppConfig>("/config");
}

export function callTool(
  toolId: string,
  input: string,
  modelConfig: ModelConfig,
  fields: Record<string, string> = {},
): Promise<ToolResponse> {
  return request<ToolResponse>(`/tools/${toolId}`, {
    method: "POST",
    body: JSON.stringify({ input, modelConfig, fields }),
  });
}

export interface StreamedBlock {
  index: number;
  title?: string | null;
  content: string;
  language?: string | null;
}

export interface StreamedError {
  index: number;
  title?: string | null;
  error: string;
  code?: string;
}

interface StreamHandlers {
  onBlock: (block: StreamedBlock) => void;
  onError?: (error: StreamedError) => void;
  onDone?: () => void;
}

// Streams a tool's result blocks as they arrive (NDJSON, one JSON object per
// line). Used by multi-result tools (Fine-Tune) so each prompt shows the moment
// its generation finishes instead of waiting for all of them.
export async function streamTool(
  toolId: string,
  input: string,
  modelConfig: ModelConfig,
  handlers: StreamHandlers,
  fields: Record<string, string> = {},
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${BASE}/api/tools/${toolId}/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input, modelConfig, fields }),
    });
  } catch {
    throw new ApiError("Network error — is the API running?", "network_error", 0);
  }

  if (!res.ok || !res.body) {
    let code = "error";
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
      code = body.code ?? code;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(detail, code, res.status);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const handleLine = (line: string) => {
    const trimmed = line.trim();
    if (!trimmed) return;
    const msg = JSON.parse(trimmed) as Record<string, unknown>;
    if (msg.done) handlers.onDone?.();
    else if (msg.error != null) handlers.onError?.(msg as unknown as StreamedError);
    else handlers.onBlock(msg as unknown as StreamedBlock);
  };

  let chunk = await reader.read();
  while (!chunk.done) {
    buffer += decoder.decode(chunk.value, { stream: true });
    let nl = buffer.indexOf("\n");
    while (nl >= 0) {
      handleLine(buffer.slice(0, nl));
      buffer = buffer.slice(nl + 1);
      nl = buffer.indexOf("\n");
    }
    chunk = await reader.read();
  }
  // Flush any trailing line without a newline terminator.
  handleLine(buffer);
}

export function callDare(
  body: { vision: string; mission: string; context: string; prompt: string },
  modelConfig: ModelConfig,
): Promise<{ content: string }> {
  return request("/dare", {
    method: "POST",
    body: JSON.stringify({ ...body, modelConfig }),
  });
}

export function callDareArtifacts(
  input: string,
  modelConfig: ModelConfig,
): Promise<{ content: string }> {
  return request("/dare/artifacts", {
    method: "POST",
    body: JSON.stringify({ input, modelConfig }),
  });
}

export function callImagePrompts(
  description: string,
  count: number,
  modelConfig: ModelConfig,
): Promise<{ prompts: string }> {
  return request("/images/prompts", {
    method: "POST",
    body: JSON.stringify({ description, count, modelConfig }),
  });
}

export function callImageGenerate(
  description: string,
  count: number,
): Promise<{ images: ImageOut[] }> {
  return request("/images/generate", {
    method: "POST",
    body: JSON.stringify({ description, count }),
  });
}
