import { useCallback, useEffect, useRef, useState } from "react";
import { isVoiceSupported, recordVoice } from "../services/voiceService";

export function useVoiceRecorder({ onBlob = null } = {}) {
  const [isRecording, setIsRecording] = useState(false);
  const [isSupported] = useState(() => isVoiceSupported());
  const [error, setError] = useState(null);
  const [blob, setBlob] = useState(null);
  const [level, setLevel] = useState(0);
  const recorderRef = useRef(null);
  const stopPromiseRef = useRef(null);
  const rafRef = useRef(null);

  useEffect(() => {
    if (!isRecording) return undefined;
    let start = performance.now();
    const tick = () => {
      const elapsed = (performance.now() - start) / 1000;
      const value = 0.35 + Math.abs(Math.sin(elapsed * 3.5)) * 0.5 + Math.random() * 0.15;
      setLevel(Math.min(1, value));
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [isRecording]);

  const start = useCallback(async () => {
    setError(null);
    setBlob(null);
    try {
      const { recorder, done } = await recordVoice({
        onStop: (newBlob) => {
          setBlob(newBlob);
          if (onBlob) onBlob(newBlob);
        },
      });
      recorderRef.current = recorder;
      stopPromiseRef.current = done;
      setIsRecording(true);
    } catch (err) {
      setError(err.message || "Microphone unavailable");
    }
  }, [onBlob]);

  const stop = useCallback(async () => {
    if (!recorderRef.current) return null;
    setIsRecording(false);
    recorderRef.current.stop();
    const result = await stopPromiseRef.current;
    recorderRef.current = null;
    stopPromiseRef.current = null;
    return result;
  }, []);

  const cancel = useCallback(() => {
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      recorderRef.current.stop();
    }
    recorderRef.current = null;
    stopPromiseRef.current = null;
    setIsRecording(false);
  }, []);

  return { isRecording, isSupported, error, blob, level, start, stop, cancel };
}
