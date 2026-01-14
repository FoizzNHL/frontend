# nhl_team_colors.py
from typing import Dict, Tuple

# HEX colors exactly from your TS file
NHL_TEAM_COLORS = {
    "ANA": {"primary": "#FF8C42", "secondary": "#C9A24D"},  # Ducks
    "ARI": {"primary": "#A62639", "secondary": "#E6D8B8"},  # Coyotes
    "BOS": {"primary": "#FFD23F", "secondary": "#000000"},  # Bruins
    "BUF": {"primary": "#0050B5", "secondary": "#FFD23F"},  # Sabres
    "CGY": {"primary": "#E3172D", "secondary": "#FFD966"},  # Flames
    "CAR": {"primary": "#E10600", "secondary": "#111111"},  # Hurricanes
    "CHI": {"primary": "#E10600", "secondary": "#000000"},  # Blackhawks
    "COL": {"primary": "#8B2A3A", "secondary": "#2A6EBB"},  # Avalanche
    "CBJ": {"primary": "#003F91", "secondary": "#E3172D"},  # Blue Jackets
    "DAL": {"primary": "#00875A", "secondary": "#A0A0A0"},  # Stars
    "DET": {"primary": "#E10600", "secondary": "#FFFFFF"},  # Red Wings
    "EDM": {"primary": "#003F91", "secondary": "#FF6A00"},  # Oilers
    "FLA": {"primary": "#003F91", "secondary": "#E3172D"},  # Panthers
    "LAK": {"primary": "#1A1A1A", "secondary": "#B3B3B3"},  # Kings
    "MIN": {"primary": "#1E6F4A", "secondary": "#C62828"},  # Wild
    "MTL": {"primary": "#E10600", "secondary": "#003DA5"},  # Canadiens (bright)
    "NSH": {"primary": "#FFD23F", "secondary": "#003F91"},  # Predators
    "NJD": {"primary": "#E10600", "secondary": "#000000"},  # Devils
    "NYI": {"primary": "#0066CC", "secondary": "#FF8C42"},  # Islanders
    "NYR": {"primary": "#0047AB", "secondary": "#E10600"},  # Rangers
    "OTT": {"primary": "#E3172D", "secondary": "#D4AF37"},  # Senators
    "PHI": {"primary": "#FF6A00", "secondary": "#000000"},  # Flyers
    "PIT": {"primary": "#FFD23F", "secondary": "#000000"},  # Penguins
    "SJS": {"primary": "#00A3AD", "secondary": "#FF8C42"},  # Sharks
    "SEA": {"primary": "#9FE0E0", "secondary": "#002033"},  # Kraken
    "STL": {"primary": "#0047AB", "secondary": "#FFD23F"},  # Blues
    "TBL": {"primary": "#0047AB", "secondary": "#FFFFFF"},  # Lightning
    "TOR": {"primary": "#0033A0", "secondary": "#FFFFFF"},  # Maple Leafs
    "VAN": {"primary": "#0033A0", "secondary": "#00A86B"},  # Canucks
    "VGK": {"primary": "#C9A24D", "secondary": "#3A3F44"},  # Golden Knights
    "WSH": {"primary": "#003F91", "secondary": "#E3172D"},  # Capitals
    "WPG": {"primary": "#003F91", "secondary": "#C62828"},  # Jets
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
