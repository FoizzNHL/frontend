#!/usr/bin/env python3
import time

import config
from log_utils import log
from lcd_display import LcdDisplay
from led_controller import LedController
from backend_client import fetch_game_now

# ✅ add this import
from nhl_client import fetch_goals

from button_controller import DelayController
from nhl_team_colors import get_team_colors
from emoji_state import pick_emoji_and_colors


def main():
    log("Script started.")

    lcd = LcdDisplay()
    leds = LedController()
    delay_ctrl = DelayController(lcd)

    lcd.show_text("NHL SCORE", "Starting...")
    time.sleep(1)
    lcd.show_delay_only(delay_ctrl.get_delay())

    last_game_id = None
    last_goal_count = None

    emoji_due_at = None
    emoji_shown_for_game_id = None

    try:
        while True:
            try:
                data = fetch_game_now(config.TEAM_ABBR)
                delay_ctrl.update()

                # ------------- NO GAME -------------
                if data.get("noGame"):
                    msg = data.get("message", "")
                    log(f"No game: {msg}")
                    lcd.show_text("NO GAME", msg[:config.LCD_COLS])
                    lcd.show_delay_only(delay_ctrl.get_delay())

                    last_game_id = None
                    last_goal_count = None
                    emoji_due_at = None
                    emoji_shown_for_game_id = None

                    t_end = time.time() + config.POLL_INTERVAL_SECONDS
                    while time.time() < t_end:
                        delay_ctrl.update()
                        time.sleep(0.05)
                    continue

                # ------------- ERROR -------------
                if not data.get("ok"):
                    log("Backend returned ok=false")
                    lcd.show_text("BACKEND ERR", "ok=false")
                    t_end = time.time() + config.POLL_INTERVAL_SECONDS
                    while time.time() < t_end:
                        delay_ctrl.update()
                        time.sleep(0.05)
                    continue

                # ------------- GAME DATA -------------
                home = data.get("home") or {}
                away = data.get("away") or {}

                home_score = int(home.get("score", 0))
                away_score = int(away.get("score", 0))

                line1 = f"{home.get('abbr')} {home_score}-{away_score} {away.get('abbr')}"
                lcd.show_text(line1, "")
                lcd.show_delay_only(delay_ctrl.get_delay())
                log(f"Score Update: {line1}")

                game_id = data.get("id")
                state = data.get("state")

                # ------------- NEW GAME -------------
                if game_id and game_id != last_game_id:
                    log(f"New game detected: {game_id}")
                    last_game_id = game_id
                    last_goal_count = None
                    emoji_shown_for_game_id = None
                    emoji_due_at = None

                # ------------- EMOJI AT GAME START (ONCE) -------------
                if game_id and emoji_shown_for_game_id != game_id:
                    try:
                        emoji, efg, ebg = pick_emoji_and_colors(data, config.TEAM_ABBR)
                        leds.matrix.emoji_animation(emoji, fg=efg, bg=ebg, pulses=4)
                        emoji_shown_for_game_id = game_id
                        log(f"Emoji shown at game start: {emoji}")
                    except Exception as e:
                        log(f"Emoji start display error: {e}")

                # ------------- GOALS (JERSEY NUMBER) -------------
                if game_id and state in ("LIVE", "CRIT", "PRE", "OFF"):
                    goals_payload = fetch_goals(game_id)

                    if goals_payload.get("ok"):
                        goals_list = goals_payload.get("goals") or []
                        goal_count = len(goals_list)

                        # baseline init
                        if last_goal_count is None:
                            last_goal_count = goal_count

                        # new goal(s)
                        elif goal_count > last_goal_count:
                            new_goals = goals_list[last_goal_count:]
                            last_goal_count = goal_count

                            last_goal = new_goals[-1]
                            scorer = last_goal.get("scorer") or {}

                            jersey = scorer.get("number")
                            scorer_team = (scorer.get("team") or "").upper()
                            my_team = (config.TEAM_ABBR or "").upper()

                            log(f"GOAL DETECTED! scorer={scorer.get('fullName')} jersey={jersey} team={scorer_team}")

                            # countdown then backlight animation
                            local_delay = delay_ctrl.get_delay()
                            lcd.show_text("GOAL DETECTED", f"Wait {local_delay}s")
                            log(f"Waiting {local_delay}s before triggering animation...")
                            for i in range(local_delay, 0, -1):
                                log(f"Countdown: {i}s remaining")
                                # keep button responsive during countdown
                                t_end = time.time() + 1
                                while time.time() < t_end:
                                    delay_ctrl.update()
                                    time.sleep(0.05)

                            if scorer_team and scorer_team != my_team:
                                lcd.show_text("GOAL AGAINST", f"{scorer_team} scored")
                                try:
                                    # use your team colors (or swap to scorer_team if you prefer)
                                    fg, bg = get_team_colors(scorer_team)
                                    leds.matrix.emoji_animation("sad", fg=fg, bg=bg, pulses=4)
                                    log("Opponent goal -> sad emoji shown. (No jersey / no flash)")
                                except Exception as e:
                                    log(f"Opponent sad emoji error: {e}")
                                    lcd.show_text("GOAL AGAINST", "EMOJI ERR")

                                # ✅ still schedule the "state of the game" emoji 20s later
                                emoji_due_at = time.time() + 20
                                log("Score-based emoji scheduled in 20 seconds (after opponent goal).")

                                continue

                            if jersey is not None and scorer_team:
                                try:
                                    jersey_int = int(jersey)
                                    fg_color, bg_color = get_team_colors(scorer_team)

                                    lcd.show_text("GOAL!!!", f"{scorer_team} #{jersey_int}")
                                    leds.goal_matrix_animation(jersey_int, fg=fg_color, bg=bg_color)

                                except Exception as e:
                                    log(f"Matrix jersey display error: {e}")
                                    lcd.show_text("GOAL!!!", "JERSEY ERR")
                            else:
                                lcd.show_text("GOAL!!!", "JERSEY N/A")

                            lcd.show_text("GOAL!!!", "GO HABS GO")
                            leds.goal_flash_sequence()

                            # ✅ schedule emoji 20s AFTER goal animation
                            emoji_due_at = time.time() + 20
                            log("Emoji scheduled in 20 seconds after goal animation.")

                # ------------- SCHEDULED EMOJI (ONCE) -------------
                if emoji_due_at is not None and time.time() >= emoji_due_at:
                    try:
                        emoji, efg, ebg = pick_emoji_and_colors(data, config.TEAM_ABBR)
                        leds.matrix.emoji_animation(emoji, fg=efg, bg=ebg, pulses=4)
                        log(f"Emoji shown (scheduled): {emoji}")
                    except Exception as e:
                        log(f"Emoji scheduled display error: {e}")
                    finally:
                        emoji_due_at = None

            except Exception as e:
                log(f"ERROR in main loop: {e}")
                err_msg = str(e)[:config.LCD_COLS]
                lcd.show_text("SCRIPT ERROR", err_msg)

            t_end = time.time() + config.POLL_INTERVAL_SECONDS
            while time.time() < t_end:
                delay_ctrl.update()
                time.sleep(0.05)

    except KeyboardInterrupt:
        log("Script interrupted by user.")
        lcd.clear()
        leds.turn_off()
        lcd.close()


if __name__ == "__main__":
    main()
