#!/usr/bin/env python3
import time

import config
from log_utils import log
from lcd_display import LcdDisplay
from led_controller import LedController
from button_controller import DelayController


def run_countdown(lcd: LcdDisplay, delay_ctrl: DelayController):
    """
    Countdown that keeps showing delay and logs, so you can test:
    - button changes
    - LCD updates
    - timing
    """
    local_delay = delay_ctrl.get_delay()
    lcd.show_text("GOAL DETECTED", f"Wait {local_delay}s")
    log(f"Waiting {local_delay}s before triggering animation...")

    # Re-read delay each second to let you change it with the button mid-countdown
    for i in range(local_delay, 0, -1):
        new_delay = delay_ctrl.get_delay()
        if new_delay != local_delay:
            local_delay = new_delay
            log(f"Delay changed -> {local_delay}s (restarting countdown)")
            lcd.show_text("GOAL DETECTED", f"Wait {local_delay}s")
            i = local_delay  # reset countdown

        log(f"Countdown: {i}s remaining")
        lcd.show_delay_only(delay_ctrl.get_delay())
        time.sleep(1)


def scenario_no_game(lcd: LcdDisplay, delay_ctrl: DelayController, seconds=6):
    log("SCENARIO: NO GAME")
    t_end = time.time() + seconds
    while time.time() < t_end:
        lcd.show_text("NO GAME", "Offline test")
        lcd.show_delay_only(delay_ctrl.get_delay())
        time.sleep(1)


def scenario_score_updates(lcd: LcdDisplay, delay_ctrl: DelayController, updates):
    """
    updates: list of tuples (home_abbr, home_score, away_abbr, away_score)
    """
    log("SCENARIO: SCORE UPDATES (no goal animation yet)")
    for (h, hs, a, as_) in updates:
        line1 = f"{h} {hs}-{as_} {a}"
        lcd.show_text(line1, "")
        lcd.show_delay_only(delay_ctrl.get_delay())
        log(f"Score Update: {line1}")
        time.sleep(2)


def scenario_goal_detected(
    lcd: LcdDisplay,
    leds: LedController,
    delay_ctrl: DelayController,
    team_abbr: str,
    home_abbr: str,
    away_abbr: str,
    start_home_score: int,
    start_away_score: int,
    goals_for_team: int = 2,
):
    """
    Simulates goal detection logic like your main.py:
    - increments the chosen team's score
    - triggers countdown + LED animations
    - shows score number on matrix (MTL score, or your TEAM_ABBR score)
    """
    log("SCENARIO: GOAL DETECTED + COUNTDOWN + ANIMATION")

    home_score = start_home_score
    away_score = start_away_score

    # Determine which side is TEAM_ABBR
    team_is_home = (home_abbr == team_abbr)

    last_team_score = home_score if team_is_home else away_score

    for g in range(goals_for_team):
        # Display current score
        line1 = f"{home_abbr} {home_score}-{away_score} {away_abbr}"
        lcd.show_text(line1, "")
        lcd.show_delay_only(delay_ctrl.get_delay())
        log(f"Score Update: {line1}")
        time.sleep(1.5)

        # Simulate a goal for TEAM_ABBR
        if team_is_home:
            home_score += 1
            team_score = home_score
        else:
            away_score += 1
            team_score = away_score

        # Detect goal (same logic)
        if team_score > last_team_score:
            log(f"GOAL DETECTED! Team score went {last_team_score} → {team_score}")

            # Show number on matrix (test your 2-color digits)
            try:
                # fg = white, bg = dim blue (tweak to test)
                leds.show_number(team_score, fg=(255, 255, 255), bg=(0, 0, 30))
                log(f"Matrix: showing number {team_score}")
            except Exception as e:
                log(f"Matrix display error: {e}")

            # countdown + animation
            run_countdown(lcd, delay_ctrl)

            lcd.show_text("GOAL!!!", "GO HABS GO")
            leds.goal_flash_sequence()

            # small pause after goal animation
            time.sleep(1.0)

        last_team_score = team_score


def scenario_all_led_tests(lcd: LcdDisplay, leds: LedController, delay_ctrl: DelayController):
    """
    Quick manual LED test menu.
    """
    log("SCENARIO: LED TESTS (manual quick sequence)")

    lcd.show_text("LED TEST", "Backlight white")
    leds.set_backlight((255, 255, 255))
    time.sleep(1)

    lcd.show_text("LED TEST", "Backlight red")
    leds.set_backlight((255, 0, 0))
    time.sleep(1)

    lcd.show_text("LED TEST", "Backlight off")
    leds.set_backlight((0, 0, 0))
    time.sleep(1)

    # Matrix numbers
    for n in [0, 1, 8, 9, 10, 27, 99]:
        lcd.show_text("MATRIX TEST", f"Num {n}")
        lcd.show_delay_only(delay_ctrl.get_delay())
        leds.show_number(n, fg=(255, 255, 255), bg=(0, 0, 30))
        time.sleep(1.2)

    lcd.show_text("LED TEST", "Done")
    time.sleep(1)


def main():
    log("OFFLINE TEST SCRIPT started.")

    lcd = LcdDisplay()
    leds = LedController()
    delay_ctrl = DelayController(lcd)

    try:
        lcd.show_text("OFFLINE TEST", "Starting...")
        time.sleep(1)
        lcd.show_delay_only(delay_ctrl.get_delay())

        # 1) No game display
        scenario_no_game(lcd, delay_ctrl, seconds=6)

        # 2) Some score updates (no goal)
        scenario_score_updates(
            lcd,
            delay_ctrl,
            updates=[
                ("CHI", 0, "DET", 0),
                ("CHI", 0, "DET", 1),
                ("CHI", 1, "DET", 1),
            ],
        )

        # 3) Full goal detection + countdown + animation (2 goals)
        scenario_goal_detected(
            lcd=lcd,
            leds=leds,
            delay_ctrl=delay_ctrl,
            team_abbr=config.TEAM_ABBR,   # uses your config team
            home_abbr=config.TEAM_ABBR,
            away_abbr="DET",
            start_home_score=1,
            start_away_score=1,
            goals_for_team=2,
        )

        # 4) LED-only tests
        scenario_all_led_tests(lcd, leds, delay_ctrl)

        lcd.show_text("OFFLINE TEST", "Finished ✅")
        time.sleep(2)

    except KeyboardInterrupt:
        log("OFFLINE TEST interrupted by user.")
    except Exception as e:
        log(f"OFFLINE TEST ERROR: {e}")
        lcd.show_text("TEST ERROR", str(e)[:config.LCD_COLS])
        time.sleep(2)
    finally:
        lcd.clear()
        leds.turn_off()
        lcd.close()
        log("OFFLINE TEST cleanup done.")


if __name__ == "__main__":
    main()
