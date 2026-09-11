import { useSyncExternalStore } from "react";

const emptySubscribe = () => () => {};

// Returns false during SSR/prerender and the first client render, true after.
// Used to gate rendering of values read from persisted (localStorage) state so
// the server HTML and first client render match (no hydration mismatch).
export function useIsClient(): boolean {
  return useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false,
  );
}
