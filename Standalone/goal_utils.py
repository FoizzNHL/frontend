# goal_utils.py
from typing import Optional, Dict, Any, List

def get_latest_scorer_number(goals_payload: Dict[str, Any]) -> Optional[int]:
    """
    goals_payload = result of fetch_goals(game_id)
    Returns scorer jersey number (int) for the most recent goal, or None.
    """
    goals: List[Dict[str, Any]] = (goals_payload.get("goals") or [])
    if not goals:
        return None

    last_goal = goals[-1]
    scorer = last_goal.get("scorer") or {}
    num = scorer.get("number")
    if num is None:
        return None

    try:
        return int(num)
    except Exception:
        return None
