// Per-tool run history, stored in localStorage (replaces the old @st.cache_data).
import type { ModelConfig, ResultBlock } from "@/lib/types";

export interface HistoryEntry {
  id: string;
  toolId: string;
  input: string;
  blocks: ResultBlock[];
  modelConfig: ModelConfig;
  ts: number;
}

const KEY_PREFIX = "pp-history:";
const MAX_PER_TOOL = 20;

function key(toolId: string) {
  return `${KEY_PREFIX}${toolId}`;
}

export function loadHistory(toolId: string): HistoryEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(key(toolId));
    return raw ? (JSON.parse(raw) as HistoryEntry[]) : [];
  } catch {
    return [];
  }
}

export function addHistory(
  toolId: string,
  entry: Omit<HistoryEntry, "id" | "ts" | "toolId">,
): HistoryEntry[] {
  if (typeof window === "undefined") return [];
  const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const next: HistoryEntry = { ...entry, id, toolId, ts: Date.now() };
  const list = [next, ...loadHistory(toolId)].slice(0, MAX_PER_TOOL);
  try {
    window.localStorage.setItem(key(toolId), JSON.stringify(list));
  } catch {
    /* quota or serialization failure — history is best-effort */
  }
  return list;
}

export function clearHistory(toolId: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(key(toolId));
}
