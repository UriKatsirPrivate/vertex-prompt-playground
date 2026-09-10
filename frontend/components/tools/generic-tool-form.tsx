"use client";

import { HelpCircle, Sparkles } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { ErrorState } from "@/components/tools/error-state";
import { HistoryDrawer } from "@/components/history/history-drawer";
import { LoadingState } from "@/components/tools/loading-state";
import { ResultList } from "@/components/tools/result-list";
import { StreamingResultGrid } from "@/components/tools/streaming-result-grid";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, callTool, streamTool } from "@/lib/api";
import { addHistory, type HistoryEntry } from "@/lib/history";
import type { ModelConfig, ResultBlock, ToolMeta } from "@/lib/types";
import { useConfigStore } from "@/store/config-store";

export function GenericToolForm({ tool }: { tool: ToolMeta }) {
  const [input, setInput] = useState("");
  const [blocks, setBlocks] = useState<ResultBlock[] | null>(null);
  const [meta, setMeta] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<unknown>(null);
  // Streaming state for multi-result tools: each slot fills as its block lands.
  const [streamSlots, setStreamSlots] = useState<(ResultBlock | null)[] | null>(null);
  const [streamErrors, setStreamErrors] = useState<(string | null)[]>([]);
  const asModelConfig = useConfigStore((s) => s.asModelConfig);
  const resultCount = tool.result_count ?? (tool.multi_result ? 4 : 1);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;
    setLoading(true);
    setError(null);
    setBlocks(null);
    setMeta(null);
    setStreamSlots(null);
    setStreamErrors([]);
    const modelConfig = asModelConfig();

    if (tool.multi_result) {
      await submitStreaming(modelConfig);
      return;
    }

    try {
      const res = await callTool(tool.id, input, modelConfig);
      setBlocks(res.blocks);
      setMeta(res.meta ?? null);
      addHistory(tool.id, { input, blocks: res.blocks, modelConfig });
    } catch (err) {
      setError(err);
      toast.error(err instanceof ApiError ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  async function submitStreaming(modelConfig: ModelConfig) {
    const slots: (ResultBlock | null)[] = Array(resultCount).fill(null);
    const errs: (string | null)[] = Array(resultCount).fill(null);
    setStreamSlots([...slots]);
    setStreamErrors([...errs]);
    try {
      await streamTool(tool.id, input, modelConfig, {
        onBlock: (b) => {
          slots[b.index] = { content: b.content, title: b.title, language: b.language };
          setStreamSlots([...slots]);
        },
        onError: (e) => {
          errs[e.index] = e.error;
          setStreamErrors([...errs]);
        },
      });
      const collected = slots.filter((s): s is ResultBlock => s != null);
      if (collected.length > 0) {
        addHistory(tool.id, { input, blocks: collected, modelConfig });
      } else {
        toast.error(errs.find((x) => x != null) ?? "Request failed");
      }
      // Leave streamSlots/streamErrors populated so the grid keeps showing
      // both the successful blocks and any per-slot errors after completion;
      // submit() resets them at the start of the next run.
    } catch (err) {
      setError(err);
      setStreamSlots(null);
      toast.error(err instanceof ApiError ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function restore(entry: HistoryEntry) {
    setInput(entry.input);
    setBlocks(entry.blocks);
    setError(null);
    setMeta(null);
    setStreamSlots(null);
  }

  return (
    <div className="space-y-6">
      <form onSubmit={submit} className="space-y-3">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={tool.placeholder || "Write your prompt here…"}
          className="min-h-44 font-mono text-sm"
        />
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Button type="submit" disabled={loading || !input.trim()}>
              <Sparkles className="size-4" />
              {loading ? "Generating…" : tool.label}
            </Button>
            {tool.help_url && (
              <a
                href={tool.help_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-xs"
              >
                <HelpCircle className="size-3.5" /> Learn more
              </a>
            )}
          </div>
          <HistoryDrawer toolId={tool.id} onRestore={restore} />
        </div>
      </form>

      {streamSlots ? (
        <StreamingResultGrid
          slots={streamSlots}
          errors={streamErrors}
          count={resultCount}
        />
      ) : loading ? (
        <LoadingState count={resultCount} />
      ) : error != null ? (
        <ErrorState error={error} />
      ) : blocks ? (
        <ResultList blocks={blocks} />
      ) : null}

      {!loading && meta && tool.output_kind === "stats" && (
        <div className="text-muted-foreground flex flex-wrap gap-4 text-sm">
          <span>Original: {String(meta.original_len)} chars</span>
          <span>Compressed: {String(meta.compressed_len)} chars</span>
          <span className="text-foreground font-medium">
            Reduction: {String(meta.reduction_pct)}%
          </span>
        </div>
      )}
    </div>
  );
}
