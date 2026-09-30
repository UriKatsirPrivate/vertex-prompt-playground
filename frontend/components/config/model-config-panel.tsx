"use client";

import { useAppConfig } from "@/components/config/app-config-provider";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Slider } from "@/components/ui/slider";
import { useIsClient } from "@/lib/use-is-client";
import { useConfigStore } from "@/store/config-store";

export function ModelConfigPanel() {
  const { config } = useAppConfig();
  const isClient = useIsClient();

  const {
    model_name,
    max_tokens,
    setModelName,
    setMaxTokens,
  } = useConfigStore();

  if (!config || !isClient) {
    return (
      <div className="space-y-3 p-3">
        <Skeleton className="h-9 w-full" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    );
  }

  const d = config.defaults;

  return (
    <div className="space-y-4 p-3">
      <div className="space-y-1.5">
        <Label className="text-muted-foreground text-xs font-semibold tracking-wide uppercase">
          Model
        </Label>
        <Select
          value={model_name}
          onValueChange={(v) => v && setModelName(v)}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select a model" />
          </SelectTrigger>
          <SelectContent>
            {config.models.map((m) => (
              <SelectItem key={m} value={m}>
                {m}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <SliderRow
        label="Max output tokens"
        value={max_tokens}
        min={d.max_tokens_range[0]}
        max={d.max_tokens_range[1]}
        step={256}
        onChange={setMaxTokens}
      />
    </div>
  );
}

function SliderRow({
  label,
  value,
  min,
  max,
  step,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <Label className="text-xs">{label}</Label>
        <span className="text-muted-foreground font-mono text-xs">{value}</span>
      </div>
      <Slider
        value={[value]}
        min={min}
        max={max}
        step={step}
        onValueChange={(v) => onChange(Array.isArray(v) ? v[0] : v)}
      />
    </div>
  );
}
