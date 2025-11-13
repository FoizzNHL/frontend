// src/lib/nhl/api.ts
const apiUrl = import.meta.env.VITE_API_URL;

/** Optional: quick guard for YYYY-MM-DD */
const isDate = (s?: string | null) => !!s && /^\d{4}-\d{2}-\d{2}$/.test(s);

const asJson = async (r: Response) => {
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
};

/**
 * Get a team's game for "now" or a specific date.
 * - Backend: GET /api/game/now?team=MTL&date=YYYY-MM-DD
 */
export async function getGameForTeam(team: string, date?: string | null) {
  const u = new URL(`${apiUrl}/api/game/now`);
  u.searchParams.set("team", String(team).toUpperCase());
  if (isDate(date)) u.searchParams.set("date", String(date));
  return asJson(await fetch(u.toString()));
}

/**
 * Get only the goal events for a game (players already enriched from roster).
 * - Backend: GET /api/game/:gameId/goals
 */
export async function getGameGoals(gameId: number | string) {
  const id = String(gameId).trim();
  return asJson(await fetch(`${apiUrl}/api/game/${id}/goals`));
}

export type BetLeg =
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

export type Bet = {
  id: string;
  type: "parlay";
  legs: BetLeg[];
  stake?: number;
};

export type BetsFile = { bets: Bet[] };

/**
 * Load bets from backend.
 * - Backend: GET /api/bets
 * - Returns: { bets: Bet[] }
 */
export async function getBets(): Promise<BetsFile> {
  return asJson(
    await fetch(`${apiUrl}/api/bets`, {
      cache: "no-store",
    })
  );
}

/**
 * Save/overwrite the bets file on the backend.
 * - Backend: PUT /api/bets
 * - Body: { bets: Bet[] }
 * - Backend response is expected to be JSON (e.g. { ok: true })
 */
export async function saveBets(
  bets: BetsFile | Bet[]
): Promise<{ ok: boolean; error?: string }> {
  const body: BetsFile = Array.isArray((bets as any).bets)
    ? (bets as BetsFile)
    : { bets: bets as Bet[] };

  return asJson(
    await fetch(`${apiUrl}/api/bets`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
  );
}