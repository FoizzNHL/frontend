# nhl_client.py
import json
import os
import time
import urllib.request
import config
from typing import Any, Dict, List, Optional

# ---- CONFIG (match your old config.cjs) ----
API_BASE = config.BACKEND_BASE_URL   # same base your node used
CACHE_TTL_SECONDS = 60                     # adjust as you like

# Optional: local roster cache folder
ROSTER_DIR = os.path.join(os.path.dirname(__file__), "rosters")  # ./rosters/MTL.json etc


# ----------------- tiny cache -----------------
_cache: Dict[str, Dict[str, Any]] = {}

def _cache_get(key: str):
    item = _cache.get(key)
    if not item:
        return None
    if time.time() > item["exp"]:
        _cache.pop(key, None)
        return None
    return item["val"]

def _cache_set(key: str, val: Any, ttl_seconds: int = CACHE_TTL_SECONDS):
    _cache[key] = {"val": val, "exp": time.time() + ttl_seconds}


# ----------------- http -----------------
def fetch_json(url: str, timeout: int = 10) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nhl-python-client/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8")
        return json.loads(data)


# ----------------- score/game now -----------------
def get_score_data(date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Equivalent to your Node getScoreData(dateStr):
      - if date_str == YYYY-MM-DD -> /score/{date}
      - else -> /score/now
    """
    if date_str and len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
        url = f"{API_BASE}/score/{date_str}"
    else:
        url = f"{API_BASE}/score/now"
    return fetch_json(url)


def find_game_for_team(team_abbr: str, date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Equivalent to Node findGameForTeam(teamAbbr, dateStr)
    Returns dict with keys: id, state, date, home{abbr,score}, away{abbr,score}
    """
    team_abbr = str(team_abbr).upper().strip()
    data = get_score_data(date_str)
    games = data.get("games") or []
    for g in games:
        home = g.get("homeTeam") or {}
        away = g.get("awayTeam") or {}
        if home.get("abbrev") == team_abbr or away.get("abbrev") == team_abbr:
            return {
                "id": g.get("id"),
                "state": g.get("gameState"),
                "date": date_str or data.get("currentDate") or g.get("gameDate"),
                "home": {"abbr": home.get("abbrev"), "score": home.get("score", 0) or 0},
                "away": {"abbr": away.get("abbrev"), "score": away.get("score", 0) or 0},
            }
    return {"id": None, "state": None, "home": None, "away": None}


def fetch_game_now(team_abbr: str, date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Drop-in replacement for your current backend_client.fetch_game_now().
    Returns the SAME SHAPE your main() expects:
      - ok, noGame?, message?, id, home, away
    """
    try:
        result = find_game_for_team(team_abbr, date_str)
        if not result.get("id"):
            return {
                "ok": True,
                "noGame": True,
                "message": f"No game found for {team_abbr.upper()} on {date_str or 'today'}",
            }

        return {"ok": True, **result}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ----------------- roster helpers -----------------
def read_roster_local(team_abbr: str) -> List[Dict[str, Any]]:
    team_abbr = str(team_abbr).upper().strip()

    candidates = [
        os.path.join(ROSTER_DIR, f"{team_abbr}.json"),
        os.path.join(ROSTER_DIR, f"{team_abbr.lower()}.json"),
    ]

    path = next((p for p in candidates if os.path.exists(p)), None)
    if not path:
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # your format: [ {id, fullName, position, number, shoots, headshot, team}, ... ]
    return data if isinstance(data, list) else []



def fetch_roster_live(team_abbr: str) -> List[Dict[str, Any]]:
    """
    Equivalent to roster.cjs live fallback logic:
      tries:
        /roster/{abbr}/current
        /club-roster/{abbr}/current
        /team/{abbr}/roster   (legacy)
    Normalizes to: {id, fullName, position, number, shoots, headshot, team}
    """
    team_abbr = str(team_abbr).upper().strip()
    urls = [
        f"{API_BASE}/roster/{team_abbr}/current",
        f"{API_BASE}/club-roster/{team_abbr}/current",
        f"{API_BASE}/team/{team_abbr}/roster",
    ]

    for u in urls:
        try:
            data = fetch_json(u)
            # club-roster shape
            if data.get("forwards") or data.get("defensemen") or data.get("goalies"):
                parts = (data.get("forwards") or []) + (data.get("defensemen") or []) + (data.get("goalies") or [])
                players = []
                for p in parts:
                    full = f"{(p.get('firstName') or {}).get('default','')} {(p.get('lastName') or {}).get('default','')}".strip()
                    players.append({
                        "id": p.get("id"),
                        "fullName": full,
                        "position": p.get("positionCode"),
                        "number": p.get("sweaterNumber"),
                        "shoots": p.get("shootsCatches"),
                        "headshot": p.get("headshot") or "",
                        "team": team_abbr,
                    })
                return players

            # legacy shape
            if isinstance(data.get("roster"), list):
                players = []
                for r in data["roster"]:
                    person = r.get("person") or {}
                    position = r.get("position") or {}
                    players.append({
                        "id": person.get("id") or r.get("id"),
                        "fullName": person.get("fullName") or r.get("fullName"),
                        "position": position.get("name") or position.get("code"),
                        "number": r.get("sweaterNumber"),
                        "shoots": r.get("shootsCatches"),
                        "headshot": r.get("headshot") or "",
                        "team": team_abbr,
                    })
                return players
        except Exception:
            pass

    return []


def get_roster(team_abbr: str, source: str = "auto") -> List[Dict[str, Any]]:
    team_abbr = str(team_abbr).upper().strip()

    if source in ("local", "auto"):
        local = read_roster_local(team_abbr)
        if local:
            return local
        if source == "local":
            return []

    # fallback only if file missing
    return fetch_roster_live(team_abbr)



# ----------------- goals (play-by-play) -----------------
def fetch_goals(game_id: str) -> Dict[str, Any]:
    """
    Equivalent to /api/game/:gameId/goals from games.cjs
    Returns:
      { ok:true, gameId, home:{abbr}, away:{abbr}, goals:[...] }
    """
    try:
        gid = str(game_id).strip()
        if not (gid.isdigit() and len(gid) == 10):
            return {"ok": False, "error": "Invalid gameId"}

        pbp = fetch_json(f"{API_BASE}/gamecenter/{gid}/play-by-play")
        home_abbr = (pbp.get("homeTeam") or {}).get("abbrev") or "HOME"
        away_abbr = (pbp.get("awayTeam") or {}).get("abbrev") or "AWAY"

        home_roster = get_roster(home_abbr, source="auto")
        away_roster = get_roster(away_abbr, source="auto")
        roster_map = {int(p["id"]): p for p in (home_roster + away_roster) if p.get("id")}

        def get_player(pid, details, fallback_team):
            if not pid:
                return None
            try:
                pid_int = int(pid)
            except Exception:
                return None
            if pid_int in roster_map:
                return roster_map[pid_int]
            # fallback minimal object like your node code
            return {
                "id": pid_int,
                "fullName": details.get("scoringPlayerName")
                           or details.get("assist1PlayerName")
                           or details.get("assist2PlayerName")
                           or "Unknown",
                "team": fallback_team,
            }

        goals_out = []
        for ev in pbp.get("plays") or []:
            if ev.get("typeDescKey") != "goal":
                continue
            d = ev.get("details") or {}
            team_abbr = d.get("eventOwnerTeamAbbrev") or home_abbr

            scorer = get_player(d.get("scoringPlayerId"), d, team_abbr)
            assist1 = get_player(d.get("assist1PlayerId"), d, team_abbr)
            assist2 = get_player(d.get("assist2PlayerId"), d, team_abbr)

            goals_out.append({
                "period": ((ev.get("periodDescriptor") or {}).get("number")),
                "timeInPeriod": ev.get("timeInPeriod"),
                "scorer": scorer,
                "assists": [a for a in [assist1, assist2] if a],
                "shotType": d.get("shotType"),
                "strength": d.get("strength"),
                "homeScore": d.get("homeScore"),
                "awayScore": d.get("awayScore"),
                "highlight": {
                    "url": d.get("highlightClipSharingUrl"),
                    "id": d.get("highlightClip"),
                },
            })

        return {
            "ok": True,
            "gameId": gid,
            "home": {"abbr": home_abbr},
            "away": {"abbr": away_abbr},
            "goals": goals_out,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ----------------- teams list -----------------
def fetch_teams() -> List[Dict[str, Any]]:
    """
    Equivalent to GET /api/teams from teams.cjs with caching.
    """
    cached = _cache_get("teams")
    if cached is not None:
        return cached

    data = fetch_json(f"{API_BASE}/teams")
    out = []
    for t in (data.get("teams") or []):
        tri = t.get("triCode")
        if not tri:
            continue
        out.append({
            "id": t.get("id"),
            "triCode": tri,
            "locationName": t.get("locationName") or "",
            "teamName": t.get("teamName") or "",
        })

    _cache_set("teams", out, ttl_seconds=CACHE_TTL_SECONDS)
    return out
