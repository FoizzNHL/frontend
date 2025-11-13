// src/components/BetValidator.tsx
import { useEffect, useMemo, useState } from "react";
import { getBets, saveBets } from "../lib/nhl/api";

type BetLeg =
  | { type: "moneyline"; teamTri: string }
  | { type: "total"; pick: "over" | "under"; line: number; teamTri?: string } // teamTri => team_total alias
  | {
      type: "team_total";
      pick: "over" | "under";
      line: number;
      teamTri: string;
    }
  | { type: "player_goal"; player: { name: string }; count?: number }
  | { type: "first_goal"; player: { name: string } }
  | { type: "first_team_to_score"; teamTri: string };

type Bet =
  | { id: string; type: "parlay"; legs: BetLeg[]; stake?: number }
  | never;

type BetsFile = { bets: Bet[] };

type BetStatus = "PENDING" | "WON" | "LOST" | "VOID";

function badgeClass(status: BetStatus) {
  switch (status) {
    case "WON":
      return "bg-emerald-500/10 text-emerald-700 border-emerald-500/30";
    case "LOST":
      return "bg-rose-500/10 text-rose-700 border-rose-500/30";
    case "PENDING":
      return "bg-amber-500/10 text-amber-700 border-amber-500/30";
    case "VOID":
      return "bg-gray-500/10 text-gray-700 border-gray-500/30";
  }
}

function fmt(status: BetStatus) {
  return status;
}

/** Count goals for a player by full name */
function countGoalsByPlayer(goals: any[] | undefined, fullName: string) {
  if (!goals?.length) return 0;
  return goals.filter(
    (g) => g?.scorer?.fullName?.toLowerCase() === fullName.toLowerCase()
  ).length;
}

/** Is first goal scored by player name? */
function isFirstGoalByPlayer(goals: any[] | undefined, fullName: string) {
  if (!goals?.length) return undefined; // no goals yet
  const first = goals[0];
  return first?.scorer?.fullName?.toLowerCase() === fullName.toLowerCase();
}

/** Is first team to score teamTri? */
function isFirstTeam(goals: any[] | undefined, teamTri: string) {
  if (!goals?.length) return undefined;
  const first = goals[0];
  return first?.scorer?.team?.toUpperCase() === teamTri.toUpperCase();
}

/** Current game totals */
function currentTotals(score: any) {
  const home = Number(score?.home?.score ?? 0);
  const away = Number(score?.away?.score ?? 0);
  return { home, away, total: home + away };
}

/** Who's the winner at final? returns team abbr or undefined if not final/tied */
function finalWinner(score: any): string | undefined {
  const state = (score?.state ?? "").toLowerCase();
  if (
    !["final", "game over", "final overtime", "final shootout"].some((s) =>
      state.includes(s)
    )
  )
    return undefined;
  const { home, away } = currentTotals(score);
  if (home === away) return undefined;
  return home > away ? score?.home?.abbr : score?.away?.abbr;
}

/** Leg validator -> status + live note (optional) */
function validateLeg(
  leg: BetLeg,
  score: any,
  goals: any
): { status: BetStatus; note?: string } {
  const state = (score?.state ?? "").toLowerCase();
  const isFinal = [
    "final",
    "game over",
    "final overtime",
    "final shootout",
  ].some((s) => state.includes(s));

  const isOff =
    state.includes("off") ||
    state === "off" ||
    state === "postponed" ||
    state === "cancelled";

  const glist: any[] = goals?.goals ?? [];
  const { home, away, total } = currentTotals(score);

  // ---- Normal evaluation first ----
  let result: { status: BetStatus; note?: string };

  switch (leg.type) {
    case "moneyline": {
      const win = finalWinner(score);
      if (win)
        result = {
          status:
            win.toUpperCase() === leg.teamTri.toUpperCase() ? "WON" : "LOST",
        };
      else
        result = {
          status: "PENDING",
          note: `Current: ${score?.away?.abbr} ${away} – ${home} ${score?.home?.abbr}`,
        };
      break;
    }

    case "total": {
      if (leg.teamTri) {
        const teamAbbr = leg.teamTri.toUpperCase();
        const teamScore =
          score?.home?.abbr === teamAbbr
            ? home
            : score?.away?.abbr === teamAbbr
            ? away
            : 0;
            

          const won =
            leg.pick === "over" ? teamScore > leg.line : teamScore < leg.line;
          result = {
            status: won ? "WON" : "LOST",
            note: `Final ${teamAbbr}: ${teamScore} vs line ${leg.line}`,
          };
        
      } else {
          const won = leg.pick === "over" ? total > leg.line : total < leg.line;
          result = {
            status: won ? "WON" : "LOST",
            note: `Final total: ${total} vs line ${leg.line}`,
          };
        
      }
      break;
    }

    case "player_goal": {
      const need = Math.max(1, Number(leg.count ?? 1));
      const have = countGoalsByPlayer(glist, leg.player.name);
        result = {
          status: have >= need ? "WON" : !isOff ?"PENDING" : "LOST",
          note: `${have}/${need} goals`,
        };
      
      break;
    }

    case "first_goal": {
      const v = isFirstGoalByPlayer(glist, leg.player.name);
      if (v === true) result = { status: "WON" };
      else if (v === false) result = { status: "LOST" };
      else result = { status: "PENDING" };
      break;
    }

    case "first_team_to_score": {
      const v = isFirstTeam(glist, leg.teamTri);
      if (v === true) result = { status: "WON" };
      else if (v === false) result = { status: "LOST" };
      else result = { status: "PENDING" };
      break;
    }

    default:
      result = { status: "VOID", note: "Unknown leg type" };
      break;
  }

  // ---- ✅ Post-process: if game is OFF and still pending, mark as LOST ----
  if (isOff && result.status === "PENDING") {
    result = { status: "LOST", note: "Game is OFF" };
  }

  return result;
}

function rollupParlay(legStatuses: BetStatus[]): BetStatus {
  if (legStatuses.every((s) => s === "VOID")) return "VOID";
  if (legStatuses.some((s) => s === "LOST")) return "LOST";
  if (legStatuses.every((s) => s === "WON" || s === "VOID")) return "WON";
  return "PENDING";
}

function legLabel(leg: BetLeg) {
  switch (leg.type) {
    case "moneyline":
      return `Moneyline ${leg.teamTri}`;
    case "total":
      return leg.teamTri
        ? `Team Total ${leg.teamTri} ${leg.pick} ${leg.line}`
        : `Total ${leg.pick} ${leg.line}`;
    case "team_total":
      return `Team Total ${leg.teamTri} ${leg.pick} ${leg.line}`;
    case "player_goal":
      return `Anytime Goal: ${leg.player.name}${
        leg.count ? ` x${leg.count}` : ""
      }`;
    case "first_goal":
      return `First Goal: ${leg.player.name}`;
    case "first_team_to_score":
      return `First Team to Score: ${leg.teamTri}`;
  }
}

export function BetValidator({
  score,
  goals,
  sourceUrl = "/data/bets.json",
}: {
  score: any;
  goals: any;
  sourceUrl?: string; // in case you want to override path
}) {
  const [bets, setBets] = useState<Bet[] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const isReady = Boolean(score) && Boolean(goals);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setErr(null);
        const json: BetsFile = await getBets();
        console.log(json.bets);
       if (alive) setBets(json.bets);
        // if (alive) setBets(data.bets ?? []);
      } catch (e: any) {
        if (alive) setErr(e?.message ?? "Failed to load bets.json");
      }
    })();
    return () => {
      alive = false;
    };
  }, [sourceUrl]);

  const rows = useMemo(() => {
    if (!bets || !isReady) return [];
    return bets.map((bet) => {
      const legsWithEval = bet.legs.map((leg) => {
        const { status, note } = validateLeg(leg, score, goals);
        return { leg, status, note };
      });
      const roll = rollupParlay(legsWithEval.map((l) => l.status));
      return { bet, legsWithEval, parlayStatus: roll };
    });
  }, [bets, isReady, score, goals]);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        {!isReady && (
          <span className="text-xs text-gray-500">
            (waiting for game & goals…)
          </span>
        )}
      </div>

      {err && (
        <div className="rounded-lg border bg-rose-50 text-rose-700 px-3 py-2 text-sm">
          {err}
        </div>
      )}

      {!err && (!bets || bets.length === 0) && (
        <div className="text-sm text-gray-500">No bets found.</div>
      )}

      {rows.map(({ bet, legsWithEval, parlayStatus }) => (
        <div
          key={bet.id}
          className="rounded-2xl border border-gray-200 bg-white/70 backdrop-blur-md shadow-sm overflow-hidden"
        >
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold text-gray-800">
                {bet.id}
              </span>
              {typeof bet.stake !== "undefined" && (
                <span className="text-xs text-gray-500">
                  Stake: {bet.stake}
                </span>
              )}
            </div>
            <span
              className={`text-xs px-2 py-1 rounded-full border ${badgeClass(
                parlayStatus
              )}`}
            >
              {fmt(parlayStatus)}
            </span>
          </div>

          <div className="divide-y divide-gray-100">
            {legsWithEval.map(({ leg, status, note }, i) => {
              const borderColor =
                status === "WON"
                  ? "border-l-4 border-emerald-500"
                  : status === "LOST"
                  ? "border-l-4 border-rose-500"
                  : status === "PENDING"
                  ? "border-l-4 border-amber-400"
                  : "border-l-4 border-gray-400";

              return (
                <div
                  key={i}
                  className={`flex items-center justify-between px-4 py-3 ${borderColor} bg-white/70`}
                >
                  <div className="text-sm text-gray-800">{legLabel(leg)}</div>
                  <div className="flex items-center gap-3">
                    {note && (
                      <span className="text-xs text-gray-500">{note}</span>
                    )}
                    <span
                      className={`text-xs px-2 py-1 rounded-full border ${badgeClass(
                        status
                      )}`}
                    >
                      {fmt(status)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
