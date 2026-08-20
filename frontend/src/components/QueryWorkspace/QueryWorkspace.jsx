import { useCallback, useEffect, useRef, useState } from "react";
import { useVoiceRecorder } from "../../hooks/useVoiceRecorder";
import { usePipeline } from "../../hooks/usePipeline";
import VoiceButton from "../VoiceButton/VoiceButton";
import Transcript from "../Transcript/Transcript";
import Pipeline from "../Pipeline/Pipeline";
import AnswerCard from "../AnswerCard/AnswerCard";
import SourceCard from "../SourceCard/SourceCard";
import { ragService } from "../../services/ragService";

export default function QueryWorkspace() {
  const { isRecording, isSupported, level, start, stop } = useVoiceRecorder();
  const { result, isProcessing, activeStage, error: pipelineError, run, reset } = usePipeline();
  const [query, setQuery] = useState(ragService.defaultQuery);
  const [lastTranscript, setLastTranscript] = useState("");
  const inputRef = useRef(null);

  const handleTranscribed = useCallback(
    async (blob) => {
      const transcription = await ragService.transcribeAudio(blob);
      setLastTranscript(transcription.transcript);
      setQuery(transcription.transcript);
      await run(transcription.transcript);
    },
    [run]
  );

  const startVoice = useCallback(async () => {
    if (isRecording) {
      await stop();
      return;
    }
    if (!isSupported) {
      inputRef.current?.focus();
      return;
    }
    setLastTranscript("");
    await start();
  }, [isRecording, isSupported, start, stop]);

  const finishVoice = useCallback(async () => {
    const blob = await stop();
    if (blob) await handleTranscribed(blob);
  }, [stop, handleTranscribed]);

  useEffect(() => {
    const onVoice = () => {
      if (isRecording) finishVoice();
      else startVoice();
    };
    const onAudio = (event) => handleTranscribed(event.detail);
    const onFocus = () => inputRef.current?.focus();
    window.addEventListener("rag:voice", onVoice);
    window.addEventListener("rag:audio", onAudio);
    window.addEventListener("rag:focus-query", onFocus);
    return () => {
      window.removeEventListener("rag:voice", onVoice);
      window.removeEventListener("rag:audio", onAudio);
      window.removeEventListener("rag:focus-query", onFocus);
    };
  }, [isRecording, startVoice, finishVoice, handleTranscribed]);

  const submit = async (event) => {
    event.preventDefault();
    if (!query.trim() || isProcessing) return;
    setLastTranscript("");
    await run(query.trim());
  };

  const sources = result?.sources || [];

  return (
    <section id="query" className="px-margin-mobile md:px-margin-desktop py-16">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-10">
          <span className="chip font-dm-sans bg-accent-yellow text-on-surface">INTERACTIVE CORE</span>
          <h2 className="font-display-serif italic font-semibold text-primary mt-4 text-4xl md:text-5xl leading-tight">
            Query Workspace
          </h2>
          <p className="font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] text-secondary mt-2">
            VOICE IN → CONTEXT OUT → GROUNDED ANSWERS
          </p>
        </div>

        <form
          onSubmit={submit}
          className="relative border-2 border-primary rounded-xl bg-surface-container-low p-4 offset-shadow flex items-center gap-3"
        >
          <VoiceButton
            isRecording={isRecording}
            isSupported={isSupported}
            onClick={startVoice}
            onStop={finishVoice}
            size="lg"
          />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Ask anything about Goa — or hold the mic…"
            className="flex-1 bg-transparent border-0 focus:ring-0 outline-none font-dm-sans text-[16px] text-on-surface placeholder:text-on-surface-variant"
            aria-label="Your question"
          />
          <button
            type="submit"
            disabled={isProcessing || !query.trim()}
            className="bg-primary text-on-primary font-dm-sans text-[12.5px] font-medium uppercase tracking-[0.08em] px-6 py-3 border-2 border-primary offset-shadow hover:bg-primary-container transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isProcessing ? "Thinking…" : "Ask"}
          </button>
        </form>

        {isRecording && (
          <div className="mt-4 max-w-xl mx-auto">
            <Transcript isRecording isSupported={isSupported} level={level} />
          </div>
        )}

        {lastTranscript && !isRecording && (
          <div className="mt-4 max-w-xl mx-auto">
            <Transcript text={lastTranscript} />
          </div>
        )}

        <div className="mt-4">
          <Pipeline activeStage={activeStage} isProcessing={isProcessing} />
        </div>

        {pipelineError && (
          <div
            role="alert"
            className="mt-6 border border-dotted border-error rounded-lg px-4 py-3 font-dm-sans text-[13px] text-error"
          >
            {pipelineError}
          </div>
        )}

        <div className="mt-8 space-y-6">
          <AnswerCard result={result} isProcessing={isProcessing} />

          {sources.length > 0 && (
            <section>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-display-serif italic font-semibold text-primary">
                  Sources ({sources.length})
                </h3>
                <span className="font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] text-secondary">
                  retrieved via {result?.engine?.vector_db || "vector search"}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sources.map((source, i) => (
                  <SourceCard key={source.chunk_id || i} source={source} index={i} />
                ))}
              </div>
            </section>
          )}

          {result && (
            <div className="text-center">
              <button
                type="button"
                onClick={reset}
                className="font-dm-sans text-[12.5px] font-medium uppercase tracking-[0.08em] text-primary border border-primary px-4 py-2 rounded-full hover:bg-primary hover:text-on-primary transition-colors"
              >
                New question
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
