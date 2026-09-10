"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo } from "react";

import { useAppConfig } from "@/components/config/app-config-provider";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Skeleton } from "@/components/ui/skeleton";
import { CATEGORY_ORDER } from "@/lib/tools";
import type { ToolMeta } from "@/lib/types";
import { cn } from "@/lib/utils";

function groupByCategory(tools: ToolMeta[]): [string, ToolMeta[]][] {
  const groups = new Map<string, ToolMeta[]>();
  for (const t of tools) {
    const list = groups.get(t.category) ?? [];
    list.push(t);
    groups.set(t.category, list);
  }
  return [...groups.entries()].sort(
    (a, b) => CATEGORY_ORDER.indexOf(a[0]) - CATEGORY_ORDER.indexOf(b[0]),
  );
}

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  const { config, loading } = useAppConfig();
  const pathname = usePathname();
  const groups = useMemo(() => groupByCategory(config?.tools ?? []), [config?.tools]);

  if (loading || !config) {
    return (
      <div className="space-y-2 p-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-8 w-full" />
        ))}
      </div>
    );
  }

  return (
    <Accordion multiple className="gap-1 p-2">
      {groups.map(([category, tools]) => (
        <AccordionItem key={category} value={category} className="border-none">
          <AccordionTrigger className="text-muted-foreground px-2 py-1.5 text-xs font-semibold tracking-wide uppercase hover:no-underline">
            {category}
          </AccordionTrigger>
          <AccordionContent className="pt-0 pb-1 [&_a]:no-underline">
            <ul className="space-y-0.5">
              {tools.map((tool) => {
                const active = pathname === tool.route;
                return (
                  <li key={tool.id}>
                    <Link
                      href={tool.route}
                      onClick={onNavigate}
                      className={cn(
                        "block rounded-md px-2 py-1.5 text-sm transition-colors",
                        active
                          ? "bg-accent text-accent-foreground font-medium"
                          : "text-muted-foreground hover:bg-accent/50 hover:text-foreground",
                      )}
                    >
                      {tool.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
}
