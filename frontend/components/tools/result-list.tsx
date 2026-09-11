"use client";

import { ResultBlock } from "@/components/tools/result-block";
import type { ResultBlock as ResultBlockType } from "@/lib/types";

// Layout switches on block count: 1 = full width, 2 = side-by-side,
// 4 (fine-tune) = 2x2 grid.
export function ResultList({ blocks }: { blocks: ResultBlockType[] }) {
  if (blocks.length === 0) return null;

  const cols =
    blocks.length >= 2 ? "grid-cols-1 lg:grid-cols-2" : "grid-cols-1";

  return (
    <div className={`grid gap-4 ${cols}`}>
      {blocks.map((b, i) => (
        <ResultBlock key={b.title ?? i} block={b} />
      ))}
    </div>
  );
}
