import { PIPELINE_STAGES } from "../../utils/constants";
import Icon from "../Icon/Icon";

export default function Pipeline({ activeStage = null, isProcessing = false, compact = false }) {
  const activeIndex = activeStage ? PIPELINE_STAGES.findIndex((s) => s.id === activeStage) : -1;

  return (
    <div className={`flex ${compact ? "gap-1" : "gap-2"} items-stretch justify-between flex-wrap`}>
      {PIPELINE_STAGES.map((stage, i) => {
        const isActive = activeStage === stage.id;
        const isDone = isProcessing && activeIndex !== -1 && i < activeIndex;
        const isPending = isProcessing && !isActive && !isDone;
        return (
          <div key={stage.id} className="flex items-center flex-1 min-w-[90px]">
            <div
              title={stage.description}
              aria-current={isActive ? "step" : undefined}
              className={`relative flex flex-col items-center gap-1 rounded-lg border-2 px-3 py-2 w-full transition-all duration-300 ${
                isActive
                  ? "border-tertiary bg-tertiary text-on-tertiary scale-[1.04] shadow-md"
                  : isDone
                    ? "border-primary bg-primary text-on-primary"
                    : isPending
                      ? "border-outline-variant bg-surface-container text-on-surface-variant opacity-55"
                      : "border-outline-variant bg-surface-container text-on-surface-variant"
              }`}
            >
              <Icon
                name={isDone ? "check" : stage.icon}
                size={20}
                fill={isDone}
                className={isActive ? "animate-pulse" : ""}
              />
              <span className="font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] text-center leading-tight">
                {compact ? stage.label.split(" ")[0] : stage.label}
              </span>
            </div>
            {!compact && i < PIPELINE_STAGES.length - 1 && (
              <span className="mx-1 hidden sm:flex items-center" aria-hidden="true">
                <span className="relative block w-5 h-0.5 rounded bg-outline-variant overflow-hidden">
                  <span
                    className={`absolute inset-y-0 left-0 bg-primary transition-all duration-500 ${
                      isDone || (isActive && activeIndex > i) ? "w-full" : "w-0"
                    }`}
                  />
                </span>
                <Icon name="arrow_forward" size={14} className={`ml-0.5 ${isDone ? "text-primary" : "text-outline-variant"}`} />
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
