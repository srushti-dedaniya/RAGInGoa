import { useCallback, useState } from "react";
import { ragService } from "../services/ragService";
import { useRAG } from "../context/RAGContext";

export function usePipeline() {
  const { setLatestQuery } = useRAG();
  const [result, setResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeStage, setActiveStage] = useState(null);
  const [error, setError] = useState(null);

  const run = useCallback(
    async (query, { topK = null } = {}) => {
      setIsProcessing(true);
      setError(null);
      setResult(null);
      try {
        const data = await ragService.runQuery(query, {
          onStage: setActiveStage,
          topK,
        });
        setResult(data);
        setLatestQuery(data);
        setActiveStage(null);
        return data;
      } catch (err) {
        setError(err.message || "Query failed");
        setActiveStage(null);
        return null;
      } finally {
        setIsProcessing(false);
      }
    },
    [setLatestQuery]
  );

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setActiveStage(null);
    setIsProcessing(false);
  }, []);

  return {
    result,
    isProcessing,
    activeStage,
    error,
    run,
    reset,
  };
}
