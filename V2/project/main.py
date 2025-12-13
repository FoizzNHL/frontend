#!/usr/bin/env python3

import time

import config
from log_utils import log
from lcd_display import LcdDisplay
from led_controller import LedController
from backend_client import fetch_game_now
from button_controller import DelayController
from matrix_number import display_number


def main():
    log("Script started.")

    lcd = LcdDisplay()
    leds = LedController()
    delay_ctrl = DelayController(lcd)

    lcd.show_text("NHL SCORE", "Starting...")
    time.sleep(1)
    lcd.show_delay_only(delay_ctrl.get_delay())

    last_mtl_score = None
    last_game_id = None

    try:
        while True:
            try:
                data = fetch_game_now(config.TEAM_ABBR)

                # ------------- NO GAME -------------
                if data.get("noGame"):
                    msg = data.get("message", "")
                    log(f"No game: {msg}")
                    lcd.show_text("NO GAME", msg[:config.LCD_COLS])
                    lcd.show_delay_only(delay_ctrl.get_delay())
                    last_mtl_score = None
                    last_game_id = None
                    time.sleep(config.POLL_INTERVAL_SECONDS)
                    continue

                # ------------- ERROR FROM BACKEND -------------
                if not data.get("ok"):
                    log("Backend returned ok=false")
                    lcd.show_text("BACKEND ERR", "ok=false")
                    time.sleep(config.POLL_INTERVAL_SECONDS)
                    continue

                # ------------- GAME DATA -------------
                home = data.get("home") or {}
                away = data.get("away") or {}

                home_score = home.get("score", 0)
                away_score = away.get("score", 0)

                line1 = f"{home.get('abbr')} {home_score}-{away_score} {away.get('abbr')}"
                lcd.show_text(line1, "")
                lcd.show_delay_only(delay_ctrl.get_delay())
                log(f"Score Update: {line1}")

                # Determine MTL score
                if home.get("abbr") == config.TEAM_ABBR:
                    mtl_score = home_score
                else:
                    mtl_score = away_score

                game_id = data.get("id")

                # New game detected
                if game_id and game_id != last_game_id:
                    log(f"New game detected: {game_id}")
                    last_game_id = game_id
                    last_mtl_score = mtl_score

                # ------------- GOAL DETECTED -------------
                if last_mtl_score is not None and mtl_score > last_mtl_score:
                    log(f"GOAL DETECTED! Score went from {last_mtl_score} → {mtl_score}")

                    local_delay = delay_ctrl.get_delay()
                    lcd.show_text("GOAL DETECTED", f"Wait {local_delay}s")

                    log(f"Waiting {local_delay}s before triggering animation...")
                    for i in range(local_delay, 0, -1):
                        log(f"Countdown: {i}s remaining")
                        time.sleep(1)

                    # Show GOAL message + run animation
                    lcd.show_text("GOAL!!!", "GO HABS GO")
                    leds.show_number(mtl_score, fg=(255,255,255), bg=(0,0,30))
                    leds.goal_flash_sequence()

                last_mtl_score = mtl_score

            except Exception as e:
                log(f"ERROR in main loop: {e}")
                err_msg = str(e)[:config.LCD_COLS]
                lcd.show_text("SCRIPT ERROR", err_msg)

            time.sleep(config.POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        log("Script interrupted by user.")
        lcd.clear()
        leds.turn_off()
        lcd.close()


if __name__ == "__main__":
    main()
