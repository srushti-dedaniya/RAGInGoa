import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { ragService } from "../services/ragService";

const RAGContext = createContext(null);

export function RAGProvider({ children }) {
  const [health, setHealth] = useState(null);
  const [lastQuery, setLastQuery] = useState(null);
  const [demoMode, setDemoMode] = useState(false);

  const refreshHealth = useCallback(async () => {
    const data = await ragService.getHealth();
    setHealth(data);
    if (data && data.service && data.status === "ONLINE") setDemoMode(false);
    return data;
  }, []);

  const setLatestQuery = useCallback((result) => {
    setLastQuery(result);
  }, []);

  useEffect(() => {
    refreshHealth();
    const timer = setInterval(refreshHealth, 30000);
    return () => clearInterval(timer);
  }, [refreshHealth]);

  const value = useMemo(
    () => ({
      health,
      demoMode,
      lastQuery,
      setLatestQuery,
      refreshHealth,
      isOnline: Boolean(health && health.status === "ONLINE"),
    }),
    [health, demoMode, lastQuery, setLatestQuery, refreshHealth]
  );

  return <RAGContext.Provider value={value}>{children}</RAGContext.Provider>;
}

export function useRAG() {
  const ctx = useContext(RAGContext);
  if (!ctx) throw new Error("useRAG must be used inside <RAGProvider>");
  return ctx;
}
