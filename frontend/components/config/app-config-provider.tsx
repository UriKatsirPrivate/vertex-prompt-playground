"use client";

import { createContext, useContext, useEffect, useState } from "react";

import { getConfig } from "@/lib/api";
import type { AppConfig } from "@/lib/types";
import { useConfigStore } from "@/store/config-store";

interface AppConfigState {
  config: AppConfig | null;
  loading: boolean;
  error: string | null;
}

const AppConfigContext = createContext<AppConfigState>({
  config: null,
  loading: true,
  error: null,
});

export function useAppConfig() {
  return useContext(AppConfigContext);
}

export function AppConfigProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AppConfigState>({
    config: null,
    loading: true,
    error: null,
  });
  const hydrateDefaults = useConfigStore((s) => s.hydrateDefaults);

  useEffect(() => {
    let active = true;
    getConfig()
      .then((config) => {
        if (!active) return;
        hydrateDefaults(
          {
            model_name: config.default_model,
            temperature: config.defaults.temperature,
            top_p: config.defaults.top_p,
            max_tokens: config.defaults.max_tokens,
          },
          config.models,
        );
        setState({ config, loading: false, error: null });
      })
      .catch((e: Error) => {
        if (!active) return;
        setState({ config: null, loading: false, error: e.message });
      });
    return () => {
      active = false;
    };
  }, [hydrateDefaults]);

  return (
    <AppConfigContext.Provider value={state}>
      {children}
    </AppConfigContext.Provider>
  );
}
