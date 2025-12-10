# backend_client.py
import requests

import config
from log_utils import log


def fetch_game_now(team_abbr: str):
    url = f"{config.BACKEND_BASE_URL}/api/game/now"
    log(f"Fetching game data: {url}?team={team_abbr}")
    resp = requests.get(url, params={"team": team_abbr}, timeout=5)
    resp.raise_for_status()
    return resp.json()
