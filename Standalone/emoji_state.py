# emoji_state.py
from typing import Tuple, Optional
from nhl_team_colors import get_team_colors

def pick_emoji_and_colors(game: dict, my_team_abbr: str):
    """
    Returns: (emoji_name, fg_rgb, bg_rgb)
      - winning: happy with my team colors
      - tied: stressed with my team colors
      - losing: sad with opponent colors
    """
    my_team_abbr = my_team_abbr.upper()

    home = game.get("home") or {}
    away = game.get("away") or {}

    home_abbr = (home.get("abbr") or "").upper()
    away_abbr = (away.get("abbr") or "").upper()

    try:
        home_score = int(home.get("score", 0))
        away_score = int(away.get("score", 0))
    except Exception:
        home_score, away_score = 0, 0

    # find opponent
    if home_abbr == my_team_abbr:
        my_score = home_score
        opp_score = away_score
        opp_abbr = away_abbr
    else:
        my_score = away_score
        opp_score = home_score
        opp_abbr = home_abbr

    if my_score > opp_score:
        emoji = "happy"
        fg, bg = get_team_colors(my_team_abbr)   # my team colors
    elif my_score < opp_score:
        emoji = "sad"
        fg, bg = get_team_colors(opp_abbr)       # opponent colors
    else:
        emoji = "stressed"
        fg, bg = get_team_colors(my_team_abbr)   # my team colors

    return emoji, fg, bg
