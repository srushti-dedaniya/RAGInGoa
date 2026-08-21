import { PIPELINE_STAGES } from "../../utils/constants";
import Icon from "../Icon/Icon";

export default function Pipeline({ activeStage = null, isProcessing = false, compact = false }) {
  const activeIndex = activeStage ? PIPELINE_STAGES.findIndex((s) => s.id === activeStage) : -1;

  return (
    <div className={`flex ${compact ? "gap-1" : "gap-2"} items-stretch justify-between flex-wrap`}>
      {PIPELINE_STAGES.map((stage, i) => {
        const isActive = activeStage === stage.id;
        const isDone = isProcessing && activeIndex !== -1 && i < activeIndex;
        const reached = activeIndex === -1 && isProcessing;
        return (
          <div key={stage.id} className="flex items-center flex-1 min-w-[90px]">
            <div
              className={`flex flex-col items-center gap-1 rounded-lg border-2 px-3 py-2 w-full transition-all ${
                isActive
                  ? "border-tertiary bg-tertiary text-on-tertiary scale-105"
                  : isDone
                    ? "border-primary bg-primary-container/20 text-primary"
                    : reached
                      ? "border-outline-variant bg-surface-container text-on-surface-variant"
                      : "border-outline-variant bg-surface-container text-on-surface-variant"
              }`}
            >
              <Icon
                name={isDone ? "check" : stage.icon}
                size={20}
                className={isActive ? "animate-pulse" : ""}
              />
              <span className="font-dm-sans text-[12px] font-medium uppercase tracking-[0.08em] text-center leading-tight">
                {compact ? stage.label.split(" ")[0] : stage.label}
              </span>
            </div>
            {!compact && i < PIPELINE_STAGES.length - 1 && (
              <span className="text-primary mx-1 hidden sm:block">
                <Icon name="arrow_forward" size={16} />
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
