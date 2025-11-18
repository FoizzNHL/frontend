import React, { useEffect, useMemo, useState } from "react";
import { getGameForTeam, getGameGoals } from "../lib/nhl/api";
import { formatDate, hexToRgb } from "../lib/utils";
import { useSound } from "../hooks/useSound";
import { useGoalWatcher } from "../hooks/useGoalWatcher";
import { useMqtt } from "../hooks/useMqtt";
import { getTeamColor } from "../lib/nhl/colors";
import { BetValidator } from "../components/BetValidator";
import ScoreCard from "../components/ScoreCard";
import { MTL_ABBR } from "../lib/constants";

export default function NhlPage() {
  const today = new Date();
  const sound = useSound();
  const PROJECTION_URL = "/goal-projection.html"; // or your route

  const [team] = useState(MTL_ABBR);
  const [disableSound] = useState<boolean>(false);
  const [date, setDate] = useState<string>(formatDate(today, "yy-mm-dd"));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
   const [goalDelaySeconds, setGoalDelaySeconds] = useState<number>(25);

  const [score, setScore] = useState<any | null>(null);
  const [goals, setGoals] = useState<any | null>(null);

  const { connected, publishJson, cmdTopic, acks } = useMqtt();

  const send = (cmd) => publishJson(cmdTopic, cmd);

  const gameId = useMemo(() => score?.id, [score]);

  async function loadGameScore(){
    const s = await getGameForTeam(team, date || undefined);
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
      updateInBettweenScoreFace();
      const g = await getGameGoals(s.id);
      setGoals(g);
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const onNewGoal = (goal: any, allGoals: any) => {
    scheduleGoalEffects(goal, allGoals);
  };

  const scheduleGoalEffects = (goal: any, allGoals: any) => {
    const delayMs = Math.max(0, goalDelaySeconds) * 1000;

    if (delayMs === 0) {
      triggerGoalEffects(goal, allGoals);
    } else {
      setTimeout(() => {
        triggerGoalEffects(goal, allGoals);
      }, delayMs);
    }
  };

  const triggerGoalEffects = (goal: any, allGoals: any) => {
    if (goal?.scorer?.team == team) {
      send({
        animation: "habs_goal",
        player_number: goal.scorer.number,
        duration: 30,
      });

      if(!disableSound) sound.play("horn");

    } else {
      const enemyColor = getTeamColor(goal.scorer.team);
      send({
        face: "sad",
        color: hexToRgb(enemyColor.primary),
        bg: hexToRgb(enemyColor.secondary),
      });

      if(!disableSound) sound.play("buuu");
    }

    loadGameScore();
    setGoals({...goals, goals: allGoals});

    setTimeout(() => {
      updateInBettweenScoreFace()
    }, 30000);
  };

  const updateInBettweenScoreFace = () => {
    if (!score) return;

    // Identify MTL side
    const isMtlHome = score.home.abbr === MTL_ABBR;
    const isMtlAway = score.away.abbr === MTL_ABBR;

    if (!isMtlHome && !isMtlAway) return; // no MTL, nothing to show

    // Extract scores
    const mtlScore = isMtlHome ? score.home.score : score.away.score;
    const oppScore = isMtlHome ? score.away.score : score.home.score;

    // Colors
    const mtlColor = getTeamColor(MTL_ABBR);
    const oppAbbr = isMtlHome ? score.away.abbr : score.home.abbr;
    const oppColor = getTeamColor(oppAbbr);

    // Determine Face
    let face = "stressed";
    let faceColor = mtlColor.primary;
    let faceBg = mtlColor.secondary;

    if (mtlScore > oppScore) {
      // Winning
      face = "happy";
      faceColor = mtlColor.primary;
      faceBg = mtlColor.secondary;
    } else if (mtlScore < oppScore) {
      // Losing
      face = "sad";
      // use opponent colors when losing
      faceColor = oppColor.primary;
      faceBg = oppColor.secondary;
    }

    send({
      face,
      color: hexToRgb(faceColor),
      bg: hexToRgb(faceBg),
    });
  };

  useGoalWatcher(gameId, onNewGoal, {
    pollMs: 4000, // poll every 4s
    fireDelayMs: 2500, // optional delay to sync with stream
    emitExistingOnStart: false,
  });

  function simulateNewGoal() {
    // if (!goals) return;
    // const fake = {
    //   ...goals.goals[1],
    //   timeInPeriod: "10:00",
    //   fake: true,
    // };
    // onNewGoal(fake, [...goals.goals, fake]); // your watcher callback

    openGoalAnimation();
  }

  const openGoalAnimation = () => {
      const goalWindow = window.open(
        PROJECTION_URL,
        "projector",
        "width=1920,height=1080"
    );

    // give the window time to load
    setTimeout(() => {
        goalWindow?.postMessage({ type: "GOAL", team: "MTL" }, "*");
    }, 500);
  }

  return (
    <div className="mx-auto max-w-3xl p-6 space-y-4">
      <div className="absolute right-2 top-2">
        <div
          className={`px-4 py-2 rounded-full border ${
            connected
              ? "bg-emerald-400/10 text-emerald-300 border-emerald-300/30"
              : "bg-rose-400/10 text-rose-300 border-rose-300/30"
          }`}
        >
          <span
            className={`inline-block w-2 h-2 rounded-full mr-2 ${
              connected ? "bg-emerald-400" : "bg-rose-400"
            } animate-pulse`}
          />
          {connected ? "Connected" : "Disconnected"}
        </div>
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          load();
        }}
        className="flex flex-wrap items-end gap-4 bg-white/70 backdrop-blur-md border border-gray-200 rounded-2xl p-4 shadow-md"
      >
        <div>
          <label className="block text-xs text-gray-600 mb-1">
            Date (YYYY-MM-DD)
          </label>
          <input
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-black bg-white/80 shadow-inner focus:ring-2 focus:ring-blue-400"
            placeholder="2025-11-06"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="h-10 px-5 rounded-lg bg-linear-to-r from-blue-600 to-blue-500 text-white font-medium shadow-md hover:opacity-90 transition disabled:opacity-50"
        >
          {loading ? "Loading…" : "Load Game"}
        </button>
        <div>
          <label className="block text-xs text-gray-600 mb-1">
            Goal delay (seconds before animation)
          </label>
          <input
            type="number"
            min={0}
            step={0.5}
            value={goalDelaySeconds}
            onChange={(e) =>
              setGoalDelaySeconds(
                Math.max(0, Number(e.target.value) || 0)
              )
            }
            className="border border-gray-300 rounded-md px-3 py-2 text-black bg-white/80 shadow-inner focus:ring-2 focus:ring-blue-400 w-32"
          />
        </div>
      </form>

      {error && (
        <div className="rounded-xl border p-4 bg-red-100 text-red-700 shadow-sm">
          {error}
        </div>
      )}

      <button
        className="h-10 px-5 rounded-lg bg-linear-to-r from-blue-600 to-blue-500 text-white font-medium shadow-md hover:opacity-90 transition disabled:opacity-50"
        onClick={simulateNewGoal}
      >
        Simulate Goal
      </button>

      {score && !score.noGame && (
        <ScoreCard score={score}/>
      )}

      {score?.noGame && (
        <div className="p-4 rounded-xl border bg-white/70 backdrop-blur-md shadow-sm text-gray-700">
          {score.message}
        </div>
      )}

      {gameId && goals && (
        <div className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-2xl border border-green-300 bg-gradient-to-b from-green-50 via-white/90 to-green-100 backdrop-blur-md shadow-md p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-3 text-center">
                {goals.home?.abbr === team ? goals.home.abbr : goals.away.abbr}{" "}
                Goals
              </h3>

              <div className="flex flex-col gap-3 max-h-[70vh] overflow-y-auto pr-2">
                {goals.goals
                  .filter((g: any) => g?.scorer?.team === team)
                  .map((goal: any, idx: number) => (
                    <div
                      key={idx}
                      className="relative rounded-xl border border-green-200 bg-white/70 p-3 shadow-sm hover:shadow-md transition"
                    >
                      <div className="flex items-center gap-3">
                        {goal.scorer?.headshot ? (
                          <img
                            src={goal.scorer.headshot}
                            alt={goal.scorer.fullName}
                            className="w-12 h-12 rounded-full border border-green-200 shadow-sm object-cover"
                          />
                        ) : (
                          <div className="w-12 h-12 rounded-full bg-green-200 flex items-center justify-center text-green-800 font-bold">
                            {goal.scorer?.number ?? "?"}
                          </div>
                        )}

                        <div className="flex-1">
                          <div className="text-sm font-semibold text-gray-800">
                            {goal.scorer?.fullName}{" "}
                            {goal.scorer?.number && (
                              <span className="text-gray-500">
                                #{goal.scorer.number}
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-600">
                            P{goal.period ?? "?"} –{" "}
                            {goal.timeInPeriod ?? "--:--"}{" "}
                            {goal.strength && (
                              <span className="ml-1 text-emerald-700 font-medium">
                                ({goal.strength})
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            Score: {goal.awayScore} – {goal.homeScore}
                          </div>
                        </div>

                        {goal.highlight?.url && (
                          <a
                            href={goal.highlight.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full border border-green-200 hover:bg-green-200 transition"
                          >
                            ▶ Watch
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            {/* ====== RIGHT COLUMN: Opponent Goals ====== */}
            <div className="rounded-2xl border border-yellow-300 bg-gradient-to-b from-yellow-50 via-white/90 to-yellow-100 backdrop-blur-md shadow-md p-4">
              <h3 className="text-lg font-semibold text-yellow-800 mb-3 text-center">
                {goals.home?.abbr === team ? goals.away.abbr : goals.home.abbr}{" "}
                Goals
              </h3>

              <div className="flex flex-col gap-3 max-h-[70vh] overflow-y-auto pr-2">
                {goals.goals
                  .filter((g: any) => g.scorer.team !== team)
                  .map((goal: any, idx: number) => (
                    <div
                      key={idx}
                      className="relative rounded-xl border border-yellow-200 bg-white/70 p-3 shadow-sm hover:shadow-md transition"
                    >
                      <div className="flex items-center gap-3">
                        {goal.scorer?.headshot ? (
                          <img
                            src={goal.scorer.headshot}
                            alt={goal.scorer.fullName}
                            className="w-12 h-12 rounded-full border border-yellow-200 shadow-sm object-cover"
                          />
                        ) : (
                          <div className="w-12 h-12 rounded-full bg-yellow-200 flex items-center justify-center text-yellow-800 font-bold">
                            {goal.scorer?.number ?? "?"}
                          </div>
                        )}

                        <div className="flex-1">
                          <div className="text-sm font-semibold text-gray-800">
                            {goal.scorer?.fullName}{" "}
                            {goal.scorer?.number && (
                              <span className="text-gray-500">
                                #{goal.scorer.number}
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-600">
                            P{goal.period ?? "?"} –{" "}
                            {goal.timeInPeriod ?? "--:--"}{" "}
                            {goal.strength && (
                              <span className="ml-1 text-yellow-700 font-medium">
                                ({goal.strength})
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            Score: {goal.awayScore} – {goal.homeScore}
                          </div>
                        </div>

                        {goal.highlight?.url && (
                          <a
                            href={goal.highlight.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full border border-yellow-200 hover:bg-yellow-200 transition"
                          >
                            ▶ Watch
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {gameId && goals && (
        <>
          {/* ... your existing Goals UI ... */}
          <div className="mt-8">
            <BetValidator score={score} goals={goals} />
          </div>
        </>
      )}
    </div>
  );
}
