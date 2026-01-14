// src/components/GoalCard.tsx
import React from "react";
import type { NhlGoal } from "../types/types";

type Props = {
  goal: NhlGoal;
  color?: string; // primary (hex)
  bg?: string;    // secondary (hex)
};

export const GoalCard: React.FC<Props> = ({ goal, color, bg }) => {
  const primary = color || "#888";
  const secondary = bg || "#ccc";

  const border = `${primary}33`;       // 20% opacity
  const accent = `${primary}CC`;       // 80% opacity
  const bubbleBg = `${secondary}33`;   // 20%
  const pillBg = `${secondary}22`;     // 13%
  const pillBorder = `${primary}44`;   // 27%

  const hasHeadshot = Boolean(goal.scorer?.headshot);

  return (
    <div
      className="relative rounded-xl p-3 shadow-sm hover:shadow-md transition backdrop-blur-md"
      style={{
        background: "rgba(255,255,255,0.55)",
        border: `1px solid ${border}`,
      }}
    >
      <div className="flex items-center gap-3">

        {/* Avatar / Bubble */}
        {hasHeadshot ? (
          <img
            src={goal.scorer?.headshot}
            alt={goal.scorer?.fullName}
            className="w-12 h-12 rounded-full border object-cover"
            style={{
              borderColor: border,
            }}
          />
        ) : (
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center font-semibold text-gray-900"
            style={{
              background: bubbleBg,
              border: `1px solid ${border}`,
            }}
          >
            {goal.scorer?.number ?? "?"}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-gray-900 truncate">
            {goal.scorer?.fullName || "Unknown"}
            {goal.scorer?.number && (
              <span className="text-gray-500"> #{goal.scorer.number}</span>
            )}
          </div>

          <div className="text-xs text-gray-600">
            P{goal.period ?? "?"} – {goal.timeInPeriod ?? "--:--"}{" "}
            {goal.strength && (
              <span style={{ color: accent }}>
                ({goal.strength})
              </span>
            )}
          </div>

          <div className="text-xs text-gray-500 mt-1">
            Score: {goal.awayScore} – {goal.homeScore}
          </div>
        </div>

        {/* Watch button */}
        {goal.highlight?.url && (
          <a
            href={goal.highlight.url}
            target="_blank"
            rel="noreferrer"
            className="text-xs px-2 py-1 rounded-full transition whitespace-nowrap backdrop-blur-md"
            style={{
              background: pillBg,
              border: `1px solid ${pillBorder}`,
              color: accent,
            }}
          >
            ▶ Watch
          </a>
        )}
      </div>
    </div>
  );
};
