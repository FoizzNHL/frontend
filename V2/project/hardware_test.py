#!/usr/bin/env python3
import time

import config
from log_utils import log
from lcd_display import LcdDisplay
from led_controller import LedController
from button_controller import DelayController
from nhl_team_colors import get_team_colors


def safe_call(name, fn):
    try:
        return fn()
    except Exception as e:
        log(f"[{name}] ERROR: {e}")
        return None


def main():
    log("Hardware test started.")

    lcd = LcdDisplay()
    leds = LedController()
    delay_ctrl = DelayController(lcd)

    # ---------- LCD BOOT ----------
    safe_call("lcd.show_text", lambda: lcd.show_text("HW TEST", "Booting..."))
    time.sleep(1)

    # Show current delay value
    d = safe_call("delay_ctrl.get_delay", lambda: delay_ctrl.get_delay())
    if d is None:
        d = 0
    safe_call("lcd.show_delay_only", lambda: lcd.show_delay_only(d))
    time.sleep(1)

    # ---------- LED OFF ----------
    safe_call("leds.turn_off", lambda: leds.turn_off())
    safe_call("lcd.show_text", lambda: lcd.show_text("LED", "OFF"))
    time.sleep(1)

    # ---------- BASIC MATRIX / STRIP TESTS ----------
    # Uses your team colors helper (pick any team abbrev you want)
    team = (config.TEAM_ABBR or "MTL").upper()
    fg, bg = get_team_colors(team)

    # 1) Emoji pulse
    safe_call("lcd.show_text", lambda: lcd.show_text("MATRIX", "Emoji test"))
    safe_call("leds.matrix.emoji_animation", lambda: leds.matrix.emoji_animation("happy", fg=fg, bg=bg, pulses=3))
    time.sleep(0.5)

    # 2) Jersey number test
    safe_call("lcd.show_text", lambda: lcd.show_text("MATRIX", "Jersey # test"))
    safe_call("leds.goal_matrix_animation", lambda: leds.goal_matrix_animation(31, fg=fg, bg=bg))
    time.sleep(0.5)

    # 3) Goal flash test (strip / whatever your LedController drives)
    safe_call("lcd.show_text", lambda: lcd.show_text("STRIP", "Flash sequence"))
    safe_call("leds.goal_flash_sequence", lambda: leds.goal_flash_sequence())
    time.sleep(0.5)

    # ---------- BUTTON / DELAY LIVE TEST ----------
    # Loop: show delay value live; if it changes, do a tiny LED pulse so you know input is working.
    safe_call("lcd.show_text", lambda: lcd.show_text("BUTTON TEST", "Change delay"))
    last_delay = None
    last_pulse_at = 0

    try:
        while True:
            d = safe_call("delay_ctrl.get_delay", lambda: delay_ctrl.get_delay())
            if d is None:
                d = 0

            # Show it on LCD (your DelayController likely already does this, but we mirror it too)
            safe_call("lcd.show_delay_only", lambda: lcd.show_delay_only(d))

            if last_delay is None:
                last_delay = d

            # If delay changed, pulse an emoji quickly as feedback
            if d != last_delay and (time.time() - last_pulse_at) > 0.8:
                log(f"Delay changed: {last_delay} -> {d}")
                safe_call("lcd.show_text", lambda: lcd.show_text("DELAY", f"{last_delay} -> {d}"))
                safe_call(
                    "leds.matrix.emoji_animation",
                    lambda: leds.matrix.emoji_animation("wink", fg=fg, bg=bg, pulses=1)
                )
                last_delay = d
                last_pulse_at = time.time()
                # go back to delay display right after
                safe_call("lcd.show_delay_only", lambda: lcd.show_delay_only(d))

            time.sleep(0.2)

    except KeyboardInterrupt:
        log("Hardware test interrupted by user.")
    finally:
        safe_call("lcd.show_text", lambda: lcd.show_text("HW TEST", "Shutting down"))
        time.sleep(0.8)
        safe_call("lcd.clear", lambda: lcd.clear())
        safe_call("leds.turn_off", lambda: leds.turn_off())
        safe_call("lcd.close", lambda: lcd.close())


if __name__ == "__main__":
    main()
