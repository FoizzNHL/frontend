# nhl_team_colors.py
from typing import Dict, Tuple

# HEX colors exactly from your TS file
NHL_TEAM_COLORS: Dict[str, Dict[str, str]] = {
    "ANA": {"primary": "#F47A38", "secondary": "#B9975B"},
    "ARI": {"primary": "#8C2633", "secondary": "#E2D6B5"},
    "BOS": {"primary": "#FFB81C", "secondary": "#000000"},
    "BUF": {"primary": "#003087", "secondary": "#FFB81C"},
    "CGY": {"primary": "#C8102E", "secondary": "#F1BE48"},
    "CAR": {"primary": "#CC0000", "secondary": "#000000"},
    "CHI": {"primary": "#CF0A2C", "secondary": "#000000"},
    "COL": {"primary": "#6F263D", "secondary": "#236192"},
    "CBJ": {"primary": "#002654", "secondary": "#CE1126"},
    "DAL": {"primary": "#006847", "secondary": "#8F8F8C"},
    "DET": {"primary": "#CE1126", "secondary": "#FFFFFF"},
    "EDM": {"primary": "#041E42", "secondary": "#FF4C00"},
    "FLA": {"primary": "#041E42", "secondary": "#C8102E"},
    "LAK": {"primary": "#111111", "secondary": "#A2AAAD"},
    "MIN": {"primary": "#154734", "secondary": "#A6192E"},
    "MTL": {"primary": "#AF1E2D", "secondary": "#192168"},
    "NSH": {"primary": "#FFB81C", "secondary": "#041E42"},
    "NJD": {"primary": "#CE1126", "secondary": "#000000"},
    "NYI": {"primary": "#00539B", "secondary": "#F47D30"},
    "NYR": {"primary": "#0038A8", "secondary": "#CE1126"},
    "OTT": {"primary": "#C8102E", "secondary": "#C69214"},
    "PHI": {"primary": "#F74902", "secondary": "#000000"},
    "PIT": {"primary": "#FFB81C", "secondary": "#000000"},
    "SJS": {"primary": "#006D75", "secondary": "#EA7200"},
    "SEA": {"primary": "#99D9D9", "secondary": "#001628"},
    "STL": {"primary": "#002F87", "secondary": "#FCB514"},
    "TBL": {"primary": "#002868", "secondary": "#FFFFFF"},
    "TOR": {"primary": "#00205B", "secondary": "#FFFFFF"},
    "VAN": {"primary": "#00205B", "secondary": "#00843D"},
    "VGK": {"primary": "#B4975A", "secondary": "#333F48"},
    "WSH": {"primary": "#041E42", "secondary": "#C8102E"},
    "WPG": {"primary": "#041E42", "secondary": "#AC162C"},
}

# ---------- helpers ----------

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """'#AF1E2D' -> (175, 30, 45)"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_team_colors(abbr: str) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """
    Returns (primary_rgb, secondary_rgb)
    Fallback = grey tones
    """
    abbr = str(abbr).upper().strip()
    colors = NHL_TEAM_COLORS.get(abbr)
    if not colors:
        return (153, 153, 153), (51, 51, 51)

    return (
        hex_to_rgb(colors["primary"]),
        hex_to_rgb(colors["secondary"]),
    )
