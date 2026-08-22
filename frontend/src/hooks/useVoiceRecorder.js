import { useCallback, useRef, useState } from "react";
import { isVoiceSupported, recordVoice } from "../services/voiceService";

export function useVoiceRecorder({ onBlob = null } = {}) {
  const [isRecording, setIsRecording] = useState(false);
  const [isSupported] = useState(() => isVoiceSupported());
  const [error, setError] = useState(null);
  const [blob, setBlob] = useState(null);
  const [level, setLevel] = useState(0);
  const recorderRef = useRef(null);
  const stopPromiseRef = useRef(null);

  const resetLevel = useCallback(() => setLevel(0), []);

  const start = useCallback(async () => {
    setError(null);
    setBlob(null);
    try {
      const { recorder, done } = await recordVoice({
        onLevel: setLevel,
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
    resetLevel();
    return result;
  }, [resetLevel]);

  const cancel = useCallback(() => {
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      recorderRef.current.stop();
    }
    recorderRef.current = null;
    stopPromiseRef.current = null;
    setIsRecording(false);
    resetLevel();
  }, [resetLevel]);

  return { isRecording, isSupported, error, blob, level, start, stop, cancel };
}
