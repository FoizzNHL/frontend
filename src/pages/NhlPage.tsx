import { useEffect, useMemo, useState } from "react";
import { getGameForTeam, getGameGoals } from "../lib/nhl/api";
import { formatDate, hexToRgb } from "../lib/utils";
import { useSound } from "../hooks/useSound";
import { useGoalWatcher } from "../hooks/useGoalWatcher";
import { useMqtt } from "../hooks/useMqtt";
import { getTeamColor } from "../lib/nhl/colors";
import { BetValidator } from "../components/BetValidator";
import ScoreCard from "../components/ScoreCard";
import { MTL_ABBR } from "../lib/constants";

import { ConnectionStatusBadge } from "../components/ConnectionStatusBadge";
import { ControlPanel } from "../components/ControlPanel";
import { GoalsPanel } from "../components/GoalsPanel";
import type {
  LedCommand,
  NhlGoal,
  NhlGoalsResponse,
  NhlScore,
} from "../types/types";

const PROJECTION_URL = "/goal-projection.html";
const TEAM_STORAGE_KEY = "nhl.selectedTeam";
const DELAY_STORAGE_KEY = "nhl.delay";

export default function NhlPage() {
  const today = new Date();
  const [team, setTeam] = useState<string>(() => {
    if (typeof window === "undefined") return MTL_ABBR;

    try {
      const stored = window.localStorage.getItem(TEAM_STORAGE_KEY);
      return stored || MTL_ABBR; // fallback to MTL
    } catch {
      return MTL_ABBR;
    }
  });

  const [disableSound] = useState<boolean>(false);
  const [date, setDate] = useState<string>(formatDate(today, "yy-mm-dd"));
  const [goalDelaySeconds, setGoalDelaySeconds] = useState<number>(() => {
    if (typeof window === "undefined") return 25;

    const storedDelay = window.localStorage.getItem(DELAY_STORAGE_KEY);
    if(!storedDelay) return 25;

    try {
      const stored = parseInt(storedDelay);
      return stored;
    } catch {
      return 25;
    }
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [score, setScore] = useState<NhlScore | null>(null);
  const [goals, setGoals] = useState<NhlGoalsResponse | null>(null);

  const sound = useSound();
  const { connected, publishJson, cmdTopic } = useMqtt();

  const send = (cmd: LedCommand) => {
    console.log(cmd);
    publishJson(cmdTopic, cmd);
  }
  const gameId = useMemo(() => score?.id, [score]);

  async function loadGameScore(selectedTeam = team, selectedDate = date) {
    const s = await getGameForTeam(selectedTeam, selectedDate || undefined);
    setScore(s);
    return s;
  }

  async function load() {
    try {
      setLoading(true);
      setError(null);
      setScore(null);
      setGoals(null);

      const s = await loadGameScore();
      if (!s?.id) return;

      const g = await getGameGoals(s.id);
      setGoals(g);
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message);
      } else if (typeof e === "string") {
        setError(e);
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    try {
      window.localStorage.setItem(TEAM_STORAGE_KEY, team);
    } catch {
      // ignore storage errors
    }
  }, [team]);

  useEffect(() => {
    try {
      window.localStorage.setItem(DELAY_STORAGE_KEY, goalDelaySeconds.toString());
    } catch {
      // ignore storage errors
    }
  }, [goalDelaySeconds]);

  useEffect(() => {
    setTimeout(() => {
      updateInBetweenScoreFace();
    }, 30000);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [score])

  const scheduleGoalEffects = (goal: NhlGoal, allGoals: NhlGoal[]) => {
    const delayMs = Math.max(0, goalDelaySeconds) * 1000;

    if (delayMs === 0) {
      triggerGoalEffects(goal, allGoals);
    } else {
      setTimeout(() => {
        triggerGoalEffects(goal, allGoals);
      }, delayMs);
    }
  };

  const triggerGoalEffects = (goal: NhlGoal, allGoals: NhlGoal[]) => {
    if (goal?.scorer?.team === team) {
      // Habs goal animation
      send({
        animation: "habs_goal",
        player_number: goal.scorer?.number,
        duration: 20,
      } as LedCommand);

      if (!disableSound) sound.play("horn");
    } else if (goal?.scorer?.team) {
      // Opponent goal → sad face with their colors
      const enemyColor = getTeamColor(goal.scorer.team);
      send({
        face: "sad",
        color: hexToRgb(enemyColor.primary),
        bg: hexToRgb(enemyColor.secondary),
      } as LedCommand);

      if (!disableSound) sound.play("buuu");
    }

    // Refresh score
    loadGameScore();

    // Safely update goals list
    setGoals((prev) =>
      prev
        ? {
            ...prev,
            goals: allGoals,
          }
        : prev
    );
  };

  const updateInBetweenScoreFace = () => {
    if (!score) return;
    if(score.state == 'FUT') return;

    const isMtlHome = score.home.abbr === team;
    const isMtlAway = score.away.abbr === team;

    if (!isMtlHome && !isMtlAway) return;

    const mtlScore = isMtlHome ? score.home.score : score.away.score;
    const oppScore = isMtlHome ? score.away.score : score.home.score;

    const mtlColor = getTeamColor(team);
    const oppAbbr = isMtlHome ? score.away.abbr : score.home.abbr;
    const oppColor = getTeamColor(oppAbbr);

    let face: "happy" | "sad" | "stressed" = "stressed";
    let faceColor = mtlColor.primary;
    let faceBg = mtlColor.secondary;

    if (mtlScore > oppScore) {
      face = "happy";
      faceColor = mtlColor.primary;
      faceBg = mtlColor.secondary;
    } else if (mtlScore < oppScore) {
      face = "sad";
      faceColor = oppColor.primary;
      faceBg = oppColor.secondary;
    }

    send({
      face,
      color: hexToRgb(faceColor),
      bg: hexToRgb(faceBg),
    } as LedCommand);
  };

  const onNewGoal = (goal: NhlGoal, allGoals: NhlGoal[]) => {
    scheduleGoalEffects(goal, allGoals);
  };

  const onGameStart = (state: string, data: NhlGoalsResponse) => {
    if(state === 'FUT'){
      send({
        face: "happy",
        color: hexToRgb(getTeamColor(team).primary),
        bg: hexToRgb(getTeamColor(team).secondary),
      } as LedCommand); 
    }

    sound.play('startup');
  };

  useGoalWatcher(gameId, onNewGoal, onGameStart, {
    pollMs: 4000,
    fireDelayMs: 2500,
    emitExistingOnStart: false,
    persistAcrossSessions: true
  });

  function simulateNewGoal() {
    // triggerGoalEffects({
    //   id: 1,
    //   gamePk: 1,
    //   scorer: {
    //     id: 1,
    //     number:13,
    //     fullName: "Cole Caulfield",
    //     team: team,
    //   },
    // } as NhlGoal, []);

    onGameStart('FUT', {} as NhlGoalsResponse);
  }

  return (
    <div className="mx-auto max-w-5xl p-6 space-y-5">
      {/* Header / status bar */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white-900">NHL Goal Watcher</h1>
          <p className="text-sm text-white-500">
            Live goals, LEDs, bets & projections for your team.
          </p>
        </div>

        <ConnectionStatusBadge connected={connected} />
      </div>

      {/* Controls */}
      <ControlPanel
        team={team}
        onTeamChange={setTeam}
        date={date}
        onDateChange={setDate}
        loading={loading}
        onReload={load}
        goalDelaySeconds={goalDelaySeconds}
        onGoalDelayChange={setGoalDelaySeconds}
      />

      {error && (
        <div className="rounded-xl border p-4 bg-red-50 text-red-700 shadow-sm text-sm">
          {error}
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <button
          className="h-10 px-5 rounded-lg bg-linear-to-r from-blue-600 to-blue-500 text-white font-medium shadow-md hover:opacity-90 transition disabled:opacity-50 cursor-pointer"
          onClick={simulateNewGoal}
        >
          Simulate Goal
        </button>

        <button
          type="button"
          onClick={updateInBetweenScoreFace}
          className="h-10 px-4 rounded-lg border border-gray-300 bg-white text-gray-700 text-sm shadow-sm hover:bg-gray-50 transition cursor-pointer"
        >
          Refresh In-Between Face
        </button>
      </div>

      {/* Score card */}
      {score && !score.noGame && <ScoreCard score={score} />}

      {score?.noGame && (
        <div className="p-4 rounded-xl border bg-white/70 backdrop-blur-md shadow-sm text-gray-700">
          {score.message}
        </div>
      )}

      {/* Goals + Bets */}
      {gameId && goals && (
        <>
          <GoalsPanel goals={goals} team={team} />

          <div className="mt-8">
            <BetValidator score={score} goals={goals} />
          </div>
        </>
      )}
    </div>
  );
}
