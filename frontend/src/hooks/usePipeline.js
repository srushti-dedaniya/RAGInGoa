import { useCallback, useState } from "react";
import { ragService } from "../services/ragService";

export function usePipeline() {
  const [result, setResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeStage, setActiveStage] = useState(null);
  const [error, setError] = useState(null);

  const run = useCallback(async (query, { topK = null, languageCode = "en-IN" } = {}) => {
    setIsProcessing(true);
    setError(null);
    setResult(null);
    try {
      const data = await ragService.runQuery(query, {
        onStage: setActiveStage,
        topK,
        languageCode,
      });
      setResult(data);
      setActiveStage(null);
      return data;
    } catch (err) {
      setError(err.message || "Query failed");
      setActiveStage(null);
      return null;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setActiveStage(null);
    setIsProcessing(false);
  }, []);

  const runVoice = useCallback(async (blob, { topK = null, languageCode = "unknown" } = {}) => {
    setIsProcessing(true); setError(null); setResult(null); setActiveStage("stt");
    try {
      const data = await ragService.runVoice(blob, { topK, languageCode });
      setResult(data); setActiveStage(null); return data;
    } catch (err) {
      setError(err.message || "Voice query failed"); setActiveStage(null); return null;
    } finally { setIsProcessing(false); }
  }, []);

  return {
    result,
    isProcessing,
    activeStage,
    error,
    run, runVoice,
    reset,
  };
}
