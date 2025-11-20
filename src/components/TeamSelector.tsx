import { useId, useMemo } from "react";
import teamsData from "../data/teams.json";

export type TeamOption = {
  name: string;
  abbr: string;
};

export type TeamSelectorProps = {
  value?: string;
  onChange?: (abbr: string) => void;
  label?: string;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  teams?: TeamOption[];
  hideLabel?: boolean;
};

const normalizeTeams = (teamList: TeamOption[]): TeamOption[] => {
  const seen = new Map<string, TeamOption>();

  for (const team of teamList) {
    if (!team?.abbr || !team?.name) continue;

    const abbr = team.abbr.trim().toUpperCase();
    const name = team.name.trim();

    if (!abbr || !name) continue;
    if (seen.has(abbr)) continue;

    seen.set(abbr, { name, abbr });
  }

  return Array.from(seen.values()).sort((a, b) =>
    a.name.localeCompare(b.name)
  );
};

const defaultTeams = normalizeTeams(teamsData as TeamOption[]);

export default function TeamSelector({
  value,
  onChange,
  label = "Team",
  placeholder = "Select a team",
  disabled = false,
  className = "",
  teams = defaultTeams,
  hideLabel = false,
}: TeamSelectorProps) {
  const selectId = useId();

  const options = useMemo(() => normalizeTeams(teams), [teams]);

  const containerClass = ["flex flex-col gap-2", className]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={containerClass}>
      {!hideLabel && (
        <label
          htmlFor={selectId}
          className="text-sm font-medium text-gray-700"
        >
          {label}
        </label>
      )}

      <div className="relative">
        <select
          id={selectId}
          value={value ?? ""}
          onChange={(event) => onChange?.(event.target.value)}
          disabled={disabled}
          className="w-full appearance-none rounded-lg border border-gray-300 bg-white py-2.5 pl-4 pr-10 text-sm text-gray-900 shadow-sm transition hover:border-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500"
        >
          <option value="">{placeholder}</option>
          {options.map((team) => (
            <option key={team.abbr} value={team.abbr}>
              {team.name} ({team.abbr})
            </option>
          ))}
        </select>

        <svg
          aria-hidden="true"
          className="pointer-events-none absolute inset-y-0 right-3 my-auto h-4 w-4 text-gray-500"
          viewBox="0 0 20 20"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path d="M6 8l4 4 4-4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
    </div>
  );
}
