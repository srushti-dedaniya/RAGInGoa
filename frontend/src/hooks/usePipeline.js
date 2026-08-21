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
    async (query, { topK = null, languageCode = "en-IN" } = {}) => {
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

  const runVoice = useCallback(async (
    blob,
    { topK = null, languageCode = "unknown", fallbackQuery = "" } = {}
  ) => {
    setIsProcessing(true); setError(null); setResult(null); setActiveStage("stt");
    try {
      const data = await ragService.runVoice(blob, { topK, languageCode });
      setResult(data); setLatestQuery(data); setActiveStage(null); return data;
    } catch (err) {
      const usableQuery = fallbackQuery.trim();
      if (err?.code === "speech_not_understood" && usableQuery) {
        setActiveStage("retrieval");
        const data = await ragService.runQuery(usableQuery, { topK, languageCode });
        const fallbackResult = { ...data, voice_fallback: true };
        setResult(fallbackResult);
        setLatestQuery(fallbackResult);
        setActiveStage(null);
        return fallbackResult;
      }
      setError(
        err?.code === "speech_not_understood"
          ? "Couldn't understand the recording. Please try again."
          : "Couldn't process the recording. Please try again."
      );
      setActiveStage(null);
      return null;
    } finally { setIsProcessing(false); }
  }, [setLatestQuery]);

  return {
    result,
    isProcessing,
    activeStage,
    error,
    run, runVoice,
    reset,
  };
}
