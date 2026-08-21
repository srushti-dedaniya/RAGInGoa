import { useEffect, useRef } from "react";
import { useVoiceRecorder } from "../../hooks/useVoiceRecorder";
import Waveform from "../Waveform/Waveform";
import Transcript from "../Transcript/Transcript";
import Icon from "../Icon/Icon";

const ORBIT_LABELS = [
  { label: "STT", className: "top-2 -left-2", delay: "0s", duration: "3s" },
  { label: "VECTOR SEARCH", className: "top-1/2 -right-14", delay: "1s", duration: "4s" },
  { label: "RAG", className: "-bottom-4 left-6", delay: "0.5s", duration: "3.5s" },
];

export default function VoiceOrb() {
  const { isRecording, isSupported, level, start, stop, cancel, error } = useVoiceRecorder();
  const svgPathRef = useRef(null);
  const voiceStarted = useRef(false);

  useEffect(() => {
    const path = svgPathRef.current;
    if (!path) return undefined;
    let length;
    try {
      length = path.getTotalLength();
    } catch {
      return undefined;
    }
    if (!Number.isFinite(length)) return undefined;
    path.style.strokeDasharray = `${length}`;
    path.style.strokeDashoffset = `${length}`;
    const animate = () => {
      path.style.transition = "stroke-dashoffset 3s ease";
      path.style.strokeDashoffset = "0";
    };
    const timer = setTimeout(animate, 600);
    return () => clearTimeout(timer);
  }, []);

  const triggerVoice = async () => {
    if (isRecording) {
      await stop();
      voiceStarted.current = false;
      return;
    }
    if (!isSupported) {
      window.dispatchEvent(new CustomEvent("rag:focus-query"));
      return;
    }
    await start();
    voiceStarted.current = true;
  };

  const finishRecording = async () => {
    if (voiceStarted.current && isRecording) {
      const blob = await stop();
      if (blob) {
        window.dispatchEvent(new CustomEvent("rag:audio", { detail: blob }));
        window.dispatchEvent(new CustomEvent("rag:voice"));
      }
      voiceStarted.current = false;
    }
  };

  return (
    <>
      <div className="relative w-full max-w-md aspect-square flex items-center justify-center">
        <div className="absolute inset-0 border border-dotted border-primary rounded-full spin-slow opacity-50" />

        {ORBIT_LABELS.map((orbit) => (
          <div
            key={orbit.label}
            className={`absolute ${orbit.className} bg-surface text-primary font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] px-2 py-1 border border-primary offset-shadow-sm animate-bounce`}
            style={{ animationDuration: orbit.duration, animationDelay: orbit.delay }}
          >
            {orbit.label}
          </div>
        ))}

        <button
          type="button"
          onClick={triggerVoice}
          onDoubleClick={finishRecording}
          className={`relative w-64 h-64 bg-primary-container organic-blob flex items-center justify-center cursor-pointer hover:scale-105 transition-transform duration-500 z-10 offset-shadow ${
            isRecording ? "ring-2 ring-tertiary" : ""
          }`}
          aria-label="Record your question"
        >
          {isRecording ? (
            <Waveform active level={level} bars={12} className="w-24" />
          ) : (
            <Icon name="mic" size={48} className="text-surface" />
          )}
          <span className="absolute inset-0 rounded-full border border-tertiary opacity-0 hover:opacity-100 transition-opacity ping-ring" />
        </button>

        <svg className="absolute inset-0 w-full h-full pointer-events-none spin-reverse" viewBox="0 0 400 400">
          <path
            id="hero-curve"
            ref={svgPathRef}
            d="M 50, 200 a 150,150 0 1,1 300,0 a 150,150 0 1,1 -300,0"
            fill="transparent"
            stroke="#00512c"
            strokeWidth="1"
            strokeDasharray="2 6"
          />
          <text className="font-dm-sans text-[10px] font-medium fill-tertiary tracking-[0.2em] uppercase">
            <textPath href="#hero-curve" startOffset="0%">
              VOICE IN • CONTEXT OUT • GROUNDED ANSWERS • VOICE IN • CONTEXT OUT • GROUNDED ANSWERS •
            </textPath>
          </text>
        </svg>
      </div>

      {isRecording && (
        <div className="mt-8 w-full max-w-md z-10">
          <Transcript isRecording isSupported level={level} />
          <div className="flex justify-center gap-4 mt-4">
            <button
              type="button"
              onClick={finishRecording}
              className="bg-primary text-on-primary font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] px-6 py-3 border-2 border-primary offset-shadow"
            >
              Ask it
            </button>
            <button
              type="button"
              onClick={cancel}
              className="bg-surface text-error font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] px-6 py-3 border-2 border-error offset-shadow"
            >
              Cancel
            </button>
          </div>
          {error && <p className="text-center font-dm-sans text-[13px] text-error mt-3">{error}</p>}
        </div>
      )}
    </>
  );
}