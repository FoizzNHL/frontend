import React from "react";
import { GoalCard } from "./GoalCard";
import type { NhlGoal, NhlGoalsResponse } from "../types/types";
import { getTeamColor } from "../lib/nhl/colors";

const makeTeamGradient = (primary: string, secondary: string) => {
  return `linear-gradient(
    to bottom,
    ${secondary}CC,
    #ffffffDD,
    ${primary}CC
  )`;
};

type Props = {
  goals: NhlGoalsResponse;
  team: string; // selected team
};

export const GoalsPanel: React.FC<Props> = ({ goals, team }) => {
  const homeAbbr = goals.home?.abbr;
  const awayAbbr = goals.away?.abbr;

  const teamGoals = goals.goals.filter((g) => g.scorer?.team === team);
  const oppGoals = goals.goals.filter((g) => g.scorer?.team !== team);

  const teamLabel = homeAbbr === team ? homeAbbr : awayAbbr;
  const oppLabel = homeAbbr === team ? awayAbbr : homeAbbr;

  // Fallbacks in case something is undefined
  const teamAbbr = teamLabel || team || homeAbbr || awayAbbr || "MTL";
  const oppAbbr = oppLabel || (homeAbbr === team ? awayAbbr : homeAbbr) || "BOS";

  const teamColors = getTeamColor(teamAbbr);
  const oppColors = getTeamColor(oppAbbr);

  return (
    <div className="mt-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Left: Selected Team */}
        <div
          className="rounded-2xl backdrop-blur-md shadow-md p-4 border"
          style={{
            borderColor: teamColors.primary,
            backgroundImage: makeTeamGradient(
              teamColors.primary,
              teamColors.secondary
            ),
          }}
        >
          <h3
            className="text-lg font-semibold mb-3 text-center"
            style={{ color: teamColors.primary }}
          >
            {teamAbbr} Goals
          </h3>

          <div className="flex flex-col gap-3 max-h-[70vh] overflow-y-auto pr-2">
            {teamGoals.map((goal, idx) => (
              <GoalCard
                key={idx}
                goal={goal}
                color={teamColors.primary}
                bg={teamColors.secondary}
              />
            ))}

            {teamGoals.length === 0 && (
              <p className="text-xs text-center" style={{ color: teamColors.primary }}>
                No goals yet for this team.
              </p>
            )}
          </div>
        </div>

        {/* Right: Opponent */}
        <div
          className="rounded-2xl backdrop-blur-md shadow-md p-4 border"
          style={{
            borderColor: oppColors.primary,
            backgroundImage: makeTeamGradient(
              oppColors.primary,
              oppColors.secondary
            ),
          }}
        >
          <h3
            className="text-lg font-semibold mb-3 text-center"
            style={{ color: oppColors.primary }}
          >
            {oppAbbr} Goals
          </h3>

          <div className="flex flex-col gap-3 max-h-[70vh] overflow-y-auto pr-2">
            {oppGoals.map((goal, idx) => (
              <GoalCard
                key={idx}
                goal={goal}
                color={oppColors.primary}
                bg={oppColors.secondary}
              />
            ))}

            {oppGoals.length === 0 && (
              <p className="text-xs text-center" style={{ color: oppColors.primary }}>
                No goals yet for this team.
              </p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
