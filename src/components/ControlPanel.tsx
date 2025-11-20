// src/components/ControlPanel.tsx
import React from "react";
import TeamSelector from "./TeamSelector";
import { useSound } from "../hooks/useSound";

type Props = {
  team: string;
  onTeamChange: (value: string) => void;
  date: string;
  onDateChange: (value: string) => void;
  loading: boolean;
  onReload: () => void;
  goalDelaySeconds: number;
  onGoalDelayChange: (value: number) => void;
};

export const ControlPanel: React.FC<Props> = ({
  team,
  onTeamChange,
  date,
  onDateChange,
  loading,
  onReload,
  goalDelaySeconds,
  onGoalDelayChange,
}) => {

  const sound = useSound();

  const handleStopSounds = () => {
    sound.stopAll();
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onReload();
      }}
      className="flex flex-wrap items-end gap-4 bg-white/80 backdrop-blur-md border border-gray-200 rounded-2xl p-4 shadow-md"
    >
      <div className="min-w-40">
        <label className="block text-xs text-gray-600 mb-1">
          Team
        </label>
        <TeamSelector
          value={team}
          onChange={(value) => onTeamChange(value)}
        />
      </div>

      <div className="min-w-40">
        <label className="block text-xs text-gray-600 mb-1">
          Date (YYYY-MM-DD)
        </label>
        <input
          value={date}
          onChange={(e) => onDateChange(e.target.value)}
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-black bg-white/80 shadow-inner focus:ring-2 focus:ring-blue-400 focus:outline-none"
          placeholder="2025-11-06"
        />
      </div>

      <div className="min-w-40">
        <label className="block text-xs text-gray-600 mb-1">
          Goal delay (seconds before animation)
        </label>
        <input
          type="number"
          min={0}
          step={0.5}
          value={goalDelaySeconds}
          onChange={(e) =>
            onGoalDelayChange(Math.max(0, Number(e.target.value) || 0))
          }
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-black bg-white/80 shadow-inner focus:ring-2 focus:ring-blue-400 focus:outline-none"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="h-10 px-5 rounded-lg bg-linear-to-r from-blue-600 to-blue-500 text-white font-medium shadow-md hover:opacity-90 transition disabled:opacity-50 cursor-pointer"
      >
        {loading ? "Loading…" : "Load Game"}
      </button>

      <button
        type="button"
        onClick={handleStopSounds}
        className="h-10 px-5 rounded-lg bg-red-600 text-white font-medium shadow-md hover:opacity-90 transition disabled:opacity-50 cursor-pointer"
      >
        Stop Sounds
      </button>
    </form>
  );
};
