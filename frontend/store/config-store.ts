// Global model configuration (model + sliders), persisted to localStorage so it
// survives navigation and reload. Read by the config panel and every tool submit.
import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { ModelConfig } from "@/lib/types";

interface ConfigState extends ModelConfig {
  initialized: boolean;
  setModelName: (name: string) => void;
  setTemperature: (v: number) => void;
  setTopP: (v: number) => void;
  setMaxTokens: (v: number) => void;
  /** Seed defaults from the server config once, without clobbering stored values. */
  hydrateDefaults: (defaults: ModelConfig, validModels: string[]) => void;
  asModelConfig: () => ModelConfig;
}

export const useConfigStore = create<ConfigState>()(
  persist(
    (set, get) => ({
      model_name: "",
      temperature: 1.0,
      top_p: 0.8,
      max_tokens: 65535,
      initialized: false,
      setModelName: (model_name) => set({ model_name }),
      setTemperature: (temperature) => set({ temperature }),
      setTopP: (top_p) => set({ top_p }),
      setMaxTokens: (max_tokens) => set({ max_tokens }),
      hydrateDefaults: (d, validModels) => {
        const current = get().model_name;
        const currentIsValid = !!current && validModels.includes(current);
        if (get().initialized) {
          // Already seeded; fill an empty or now-invalid model name (e.g. a
          // model removed from the server list since it was persisted).
          if (!currentIsValid) set({ model_name: d.model_name });
          return;
        }
        set({
          model_name: currentIsValid ? current : d.model_name,
          temperature: d.temperature,
          top_p: d.top_p,
          max_tokens: d.max_tokens,
          initialized: true,
        });
      },
      asModelConfig: () => {
        const s = get();
        return {
          model_name: s.model_name,
          temperature: s.temperature,
          top_p: s.top_p,
          max_tokens: s.max_tokens,
        };
      },
    }),
    {
      name: "pp-model-config",
      partialize: (s) => ({
        model_name: s.model_name,
        temperature: s.temperature,
        top_p: s.top_p,
        max_tokens: s.max_tokens,
        initialized: s.initialized,
      }),
    },
  ),
);
