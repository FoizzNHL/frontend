// src/hooks/useGoalWatcher.ts
import { useEffect, useRef } from "react";
import { getGameGoals } from "../lib/nhl/api";

/** Build a stable goal id even if the API doesn't give one */
function goalKey(g: any): string {
  // Prefer an explicit id if the feed has it
  if (g.id) return String(g.id);

  // Fallback: compose a deterministic key from typical fields
  const parts = [
    g.gamePk ?? "",
    g.period ?? "",
    g.timeInPeriod ?? "",
    g.scorer?.id ?? g.scorer?.fullName ?? "",
    g.scorer?.team ?? "",
    g.awayScore ?? "",
    g.homeScore ?? "",
  ];
  return parts.join("|");
}

/** Return all goals present in `next` that weren't in `prev` (by key) */
function diffNewGoals(prevList: any[] = [], nextList: any[] = []) {
  const prevKeys = new Set(prevList.map(goalKey));
  return nextList.filter((g) => !prevKeys.has(goalKey(g)));
}

export type GoalWatcherOptions = {
  /** Polling period in milliseconds (default: 4000) */
  pollMs?: number;
  /** Optional delay before firing the callback (e.g., to sync with TV stream) */
  fireDelayMs?: number;
  /** If true, emit *all* current goals once the watcher starts */
  emitExistingOnStart?: boolean;
};

/**
 * Watch a game's goals and call `onNewGoal` whenever a new goal appears.
 * Cleans up automatically when `gameId` or component changes.
 */
export function useGoalWatcher(
  gameId: number | string | undefined | null,
  onNewGoal: (goal: any, allGoals: any[]) => void,
  opts: GoalWatcherOptions = {}
) {
  const { pollMs = 4000, fireDelayMs = 0, emitExistingOnStart = false } = opts;

  // Keep previous goal list and a live callback ref (avoids stale closures)
  const prevGoalsRef = useRef<any[] | null>(null);
  const cbRef = useRef(onNewGoal);
  cbRef.current = onNewGoal;

  useEffect(() => {
    if (!gameId) return;

    let cancelled = false;
    let timer: any = null;

    async function tick(initial = false) {
      try {
        const data = await getGameGoals(gameId);
        const nextGoals: any[] = data?.goals ?? [];

        const prev = prevGoalsRef.current ?? [];
        let newOnes = diffNewGoals(prev, nextGoals);

        // Optionally emit everything on first run (useful if you want to rebuild state)
        if (initial && emitExistingOnStart && nextGoals.length) {
          newOnes = nextGoals;
        }

        prevGoalsRef.current = nextGoals;

        // Fire callbacks (optionally delayed)
        if (!cancelled && newOnes.length) {
          const fire = () => {
            if (cancelled) return;
            for (const g of newOnes) {
              cbRef.current(g, nextGoals);
            }
          };

          if (fireDelayMs > 0) {
            setTimeout(fire, fireDelayMs);
          } else {
            fire();
          }
        }
      } catch {
        // Swallow errors here to keep polling; surface them where you fetch if needed
      } finally {
        if (!cancelled) {
          timer = setTimeout(tick, pollMs);
        }
      }
    }

    // Reset state when game changes and start polling
    prevGoalsRef.current = null;
    tick(true);

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [gameId, pollMs, fireDelayMs, emitExistingOnStart]);
}
