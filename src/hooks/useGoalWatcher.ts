// src/hooks/useGoalWatcher.ts
import { useEffect, useRef } from "react";
import { getGameForTeam, getGameGoals } from "../lib/nhl/api";
import type {
  NhlGoal,
  NhlGoalsResponse,
  NhlGoalScorer,
  NhlScore,
} from "../types/types";

const STORAGE_KEY = "goalWatcher.seenGoals";

type SeenGoalsStore = Record<string, string[]>;

type GoalWithMeta = NhlGoal & {
  id?: string | number;
  gamePk?: string | number;
  scorer?: NhlGoalScorer & { id?: string | number };
};

/** Build a stable goal id using only immutable properties */
function goalKey(g: GoalWithMeta): string {
  if (g.id != null) return String(g.id);

  // Only use properties that won't change after the goal is scored
  const parts = [
    g.gamePk ?? "",
    g.period ?? "",
    g.scorer?.team ?? "", // Team scoring the goal (won't change)
  ];

  return parts.join("|");
}

/** Return all goals present in `next` that weren't in `prev` (by key) */
function diffNewGoals(
  prevList: GoalWithMeta[] = [],
  nextList: GoalWithMeta[] = []
): GoalWithMeta[] {
  const prevKeys = new Set(prevList.map(goalKey));
  return nextList.filter((g) => !prevKeys.has(goalKey(g)));
}

function safeLoadStore(): SeenGoalsStore {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") {
      return parsed as SeenGoalsStore;
    }
    return {};
  } catch {
    return {};
  }
}

function safeSaveStore(store: SeenGoalsStore): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch {
    // ignore storage failures
  }
}

function loadSeenKeys(gameId: string | number): Set<string> {
  const store = safeLoadStore();
  const key = String(gameId);
  const arr = store[key] ?? [];
  return new Set(arr);
}

function saveSeenKeys(gameId: string | number, goals: NhlGoal[]): void {
  const store = safeLoadStore();
  const key = String(gameId);
  const existing = new Set(store[key] ?? []);
  for (const g of goals) {
    existing.add(goalKey(g as GoalWithMeta));
  }
  store[key] = Array.from(existing);
  safeSaveStore(store);
}

export type GoalWatcherOptions = {
  /** Polling period in milliseconds (default: 4000) */
  pollMs?: number;
  /** Optional delay before firing the callback (e.g., to sync with TV stream) */
  fireDelayMs?: number;
  /** If true, emit *all* current goals once the watcher starts */
  emitExistingOnStart?: boolean;
  /** If true, remember processed goals across reloads (default: true) */
  persistAcrossSessions?: boolean;
  onGameStart?: (gameState: string, data: NhlGoalsResponse) => void;
};

/**
 * Watch a game's goals and call `onNewGoal` whenever a new goal appears.
 * Persists which goals were already emitted so we don't replay animations
 * on refresh / navigation.
 */
export function useGoalWatcher(
  gameId: number | string | undefined | null,
  onNewGoal: (goal: NhlGoal, allGoals: NhlGoal[]) => void,
  onGameStart?: (gameState: string, data: NhlGoalsResponse) => void,
  opts: GoalWatcherOptions = {}
): void {
  const {
    pollMs = 4000,
    fireDelayMs = 0,
    emitExistingOnStart = false,
    persistAcrossSessions = true,
  } = opts;

  const prevGoalsRef = useRef<NhlGoal[] | null>(null);
  const prevGameStateRef = useRef<string | null>(null);

  const cbRef = useRef(onNewGoal);
  cbRef.current = onNewGoal;

  const gameStartCbRef = useRef<GoalWatcherOptions["onGameStart"]>(null);
  gameStartCbRef.current = onGameStart;

  useEffect(() => {
    if (!gameId) return;

    let cancelled = false;
    let timer: number | undefined;

    async function tick(initial: boolean): Promise<void> {
      try {
        const data: NhlGoalsResponse = await getGameGoals(gameId as string | number);
        const nextGoals: NhlGoal[] = data?.goals ?? [];

        let prev = prevGoalsRef.current;

        // First run for this game in this mount
        if (prev == null) {
          if (persistAcrossSessions) {
            const seenKeys = loadSeenKeys(gameId  as string | number);
            prev = nextGoals.filter((g) =>
              seenKeys.has(goalKey(g as GoalWithMeta))
            );
          } else {
            prev = [];
          }
        }

        try {
          const gameScore = await getGameForTeam(gameId?.toString() || "");
          const state: string | undefined = (gameScore as NhlScore)?.state;
          
          if (state) {
            const prevState = prevGameStateRef.current;
            const gameStartCb = gameStartCbRef.current;
          
            const isPreGame = (s: string | null | undefined) =>
              s === "FUT" || s === "PRE" || s === "PREGAME";
          
            if (prevState === null) {
              // First tick for this game
              prevGameStateRef.current = state;
          
              // If we *already* are in a live/playing state when we first connect,
              // treat it as "game started" so the user still gets the sound.
              if (!isPreGame(state) && !cancelled && gameStartCb) {
                gameStartCb(state, data);
              }
            } else if (isPreGame(prevState) && !isPreGame(state)) {
              // Transition from pre-game (FUT/PRE) to live/post (LIVE/IN/1ST/etc.)
              prevGameStateRef.current = state;
              if (!cancelled && gameStartCb) {
                gameStartCb(state, data);
              }
            } else if (prevState !== state) {
              // Just keep it up to date
              prevGameStateRef.current = state;
            }
          }
        } catch {
          // If game state fetch fails, continue with goal checking
        }

        let newOnes = diffNewGoals(
          prev as GoalWithMeta[],
          nextGoals as GoalWithMeta[]
        );

        // If we explicitly want to emit all existing goals at start
        if (initial && emitExistingOnStart && nextGoals.length) {
          newOnes = nextGoals as GoalWithMeta[];
        }

        if (initial && !emitExistingOnStart) {
          newOnes = [];
        }

        prevGoalsRef.current = nextGoals;

        // Persist updated seen goals (all that currently exist)
        if (persistAcrossSessions) {
          saveSeenKeys(gameId as string | number, nextGoals);
        }

        // Fire callbacks (optionally delayed)
        if (!cancelled && newOnes.length) {
          const fire = () => {
            if (cancelled) return;
            for (const g of newOnes) {
              cbRef.current(g, nextGoals);
            }
          };

          if (fireDelayMs > 0) {
            window.setTimeout(fire, fireDelayMs);
          } else {
            fire();
          }
        }
      } catch {
        // keep polling even if one request fails
        
      } finally {
        if (!cancelled) {
          timer = window.setTimeout(() => {
            void tick(false);
          }, pollMs);
        }
      }
    }

    prevGoalsRef.current = null;
    prevGameStateRef.current = null;
    void tick(true);

    return () => {
      cancelled = true;
      if (timer !== undefined) window.clearTimeout(timer);
    };
  }, [gameId, pollMs, fireDelayMs, emitExistingOnStart, persistAcrossSessions]);
}