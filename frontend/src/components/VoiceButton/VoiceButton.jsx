import Icon from "../Icon/Icon";

export default function VoiceButton({
  isRecording = false,
  isSupported = true,
  isProcessing = false,
  onClick,
  onStop,
  size = "md",
  className = "",
}) {
  const sizeClass = size === "lg" ? "w-16 h-16" : "w-12 h-12";

  return (
    <button
      type="button"
      onClick={isRecording ? onStop : onClick}
      disabled={!isSupported || isProcessing}
      title={isProcessing ? "Processing voice" : isSupported ? (isRecording ? "Stop recording" : "Start recording") : "Microphone unavailable"}
      aria-label={isProcessing ? "Processing voice" : isRecording ? "Stop recording" : "Start recording"}
      className={`${sizeClass} rounded-full flex items-center justify-center border-2 transition-all ${
        isRecording
          ? "bg-tertiary text-on-tertiary border-tertiary ping-ring"
          : "bg-primary-container text-surface border-primary offset-shadow-sm"
      } disabled:opacity-40 disabled:cursor-not-allowed ${className}`}
    >
      <Icon name={isProcessing ? "progress_activity" : isRecording ? "stop" : "mic"} size={26} fill={isRecording} className={isProcessing ? "animate-spin" : ""} />
    </button>
  );
}
