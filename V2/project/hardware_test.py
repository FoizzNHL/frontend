#!/usr/bin/env python3
import time

import config
from log_utils import log
from led_controller import LedController
from nhl_team_colors import get_team_colors


def safe_call(name, fn):
    try:
        return fn()
    except Exception as e:
        log(f"[{name}] ERROR: {e}")
        return None


def main():
    log("LED test started.")

    leds = LedController()

    # Make sure everything starts OFF
    safe_call("leds.turn_off", lambda: leds.turn_off())
    time.sleep(1)

    # Use team colors (or any colors you like)
    team = (config.TEAM_ABBR or "MTL").upper()
    fg, bg = get_team_colors(team)

    # -----------------------------
    # 1) Solid color test (strip)
    # -----------------------------
    log("Solid color test")
    safe_call("goal_flash_sequence", lambda: leds.goal_flash_sequence())
    time.sleep(2)

    # -----------------------------
    # 2) Matrix emoji test
    # -----------------------------
    log("Matrix emoji test")
    safe_call(
        "emoji_animation",
        lambda: leds.matrix.emoji_animation("happy", fg=fg, bg=bg, pulses=3)
    )
    time.sleep(1)

    # -----------------------------
    # 3) Jersey number test
    # -----------------------------
    log("Matrix jersey number test")
    safe_call(
        "goal_matrix_animation",
        lambda: leds.goal_matrix_animation(31, fg=fg, bg=bg)
    )
    time.sleep(2)

    # -----------------------------
    # 4) Loop pattern test
    # -----------------------------
    log("Loop test (CTRL+C to stop)")
    try:
        while True:
            safe_call("flash", lambda: leds.goal_flash_sequence())
            time.sleep(1)

            safe_call(
                "emoji",
                lambda: leds.matrix.emoji_animation("wink", fg=fg, bg=bg, pulses=1)
            )
            time.sleep(1)

    except KeyboardInterrupt:
        log("LED test interrupted by user.")
    finally:
        safe_call("leds.turn_off", lambda: leds.turn_off())


if __name__ == "__main__":
    main()
