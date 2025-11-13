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
