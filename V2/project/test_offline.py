#!/usr/bin/env python3
import time

import config
from log_utils import log
from lcd_display import LcdDisplay
from led_controller import LedController
from button_controller import DelayController

from nhl_team_colors import get_team_colors


def countdown_with_button(lcd: LcdDisplay, delay_ctrl: DelayController):
    """
    Countdown that keeps updating LCD and allows delay changes while testing.
    """
    local_delay = delay_ctrl.get_delay()
    lcd.show_text("GOAL DETECTED", f"Wait {local_delay}s")
    log(f"Waiting {local_delay}s before triggering animation...")

    # Allow changing delay mid-countdown
    remaining = local_delay
    while remaining > 0:
        new_delay = delay_ctrl.get_delay()
        if new_delay != local_delay:
            local_delay = new_delay
            remaining = local_delay
            log(f"Delay changed -> {local_delay}s (restart countdown)")
            lcd.show_text("GOAL DETECTED", f"Wait {local_delay}s")

        log(f"Countdown: {remaining}s remaining")
        lcd.show_delay_only(delay_ctrl.get_delay())
        time.sleep(1)
        remaining -= 1


def scenario_no_game(lcd: LcdDisplay, delay_ctrl: DelayController, seconds=6):
    log("SCENARIO: NO GAME")
    end = time.time() + seconds
    while time.time() < end:
        lcd.show_text("NO GAME", "Offline test")
        lcd.show_delay_only(delay_ctrl.get_delay())
        time.sleep(1)


def scenario_score_updates(lcd: LcdDisplay, delay_ctrl: DelayController, updates):
    log("SCENARIO: SCORE UPDATES (no goal)")
    for (h, hs, a, as_) in updates:
        line1 = f"{h} {hs}-{as_} {a}"
        lcd.show_text(line1, "")
        lcd.show_delay_only(delay_ctrl.get_delay())
        log(f"Score Update: {line1}")
        time.sleep(2)


def scenario_goal_events(
    lcd: LcdDisplay,
    leds: LedController,
    delay_ctrl: DelayController,
    events,
):
    """
    events: list of dicts like:
      {
        "home_abbr": "MTL",
        "away_abbr": "WSH",
        "home_score": 0,
        "away_score": 1,
        "scorer": { "fullName": "...", "team": "WSH", "number": 8 }
      }
    Simulates: new goal -> show jersey number with team colors -> countdown -> animation
    """
    log("SCENARIO: GOAL EVENTS (jersey # + team colors)")

    for ev in events:
        home_abbr = ev["home_abbr"]
        away_abbr = ev["away_abbr"]
        hs = ev["home_score"]
        aws = ev["away_score"]
        scorer = ev.get("scorer") or {}

        # show score line
        line1 = f"{home_abbr} {hs}-{aws} {away_abbr}"
        lcd.show_text(line1, "")
        lcd.show_delay_only(delay_ctrl.get_delay())
        log(f"Score Update: {line1}")
        time.sleep(1.5)

        # "goal detected"
        jersey = scorer.get("number")
        team = scorer.get("team")
        name = scorer.get("fullName", "Unknown")

        log(f"GOAL DETECTED! scorer={name} jersey={jersey} team={team}")

        # show jersey number on matrix with team colors
        if jersey is not None and team:
            try:
                jersey_int = int(jersey)
                fg, bg = get_team_colors(team)

                lcd.show_text("GOAL!!!", f"{team} #{jersey_int}")
                leds.show_number(jersey_int, fg=fg, bg=bg)

                log(f"Matrix: showing #{jersey_int} (FG={fg}, BG={bg})")
            except Exception as e:
                log(f"Matrix display error: {e}")
                lcd.show_text("GOAL!!!", "Matrix ERR")
        else:
            lcd.show_text("GOAL!!!", "Jersey N/A")

        # countdown then animation
        countdown_with_button(lcd, delay_ctrl)

        lcd.show_text("GOAL!!!", "GO HABS GO")
        leds.goal_flash_sequence()
        time.sleep(1.0)


def scenario_led_smoke_tests(lcd: LcdDisplay, leds: LedController, delay_ctrl: DelayController):
    log("SCENARIO: LED SMOKE TESTS")

    lcd.show_text("LED TEST", "Backlight W")
    leds.set_backlight((255, 255, 255))
    time.sleep(1)

    lcd.show_text("LED TEST", "Backlight R")
    leds.set_backlight((255, 0, 0))
    time.sleep(1)

    lcd.show_text("LED TEST", "Backlight off")
    leds.set_backlight((0, 0, 0))
    time.sleep(1)

    # matrix sample numbers using a fixed team color
    fg, bg = get_team_colors("MTL")
    for n in [0, 1, 8, 9, 10, 22, 27, 73, 88, 99]:
        lcd.show_text("MATRIX TEST", f"Num {n}")
        lcd.show_delay_only(delay_ctrl.get_delay())
        leds.show_number(n, fg=fg, bg=bg)
        time.sleep(1.0)

    lcd.show_text("LED TEST", "Done")
    time.sleep(1)


def main():
    log("OFFLINE TEST SCRIPT (jersey + team colors) started.")

    lcd = LcdDisplay()
    leds = LedController()
    delay_ctrl = DelayController(lcd)

    try:
        lcd.show_text("OFFLINE TEST", "Starting...")
        time.sleep(1)
        lcd.show_delay_only(delay_ctrl.get_delay())

        # 1) No game
        scenario_no_game(lcd, delay_ctrl, seconds=5)

        # 2) Score updates (no goal)
        scenario_score_updates(
            lcd,
            delay_ctrl,
            updates=[
                ("MTL", 0, "WSH", 0),
                ("MTL", 0, "WSH", 1),
                ("MTL", 1, "WSH", 1),
            ],
        )

        # 3) Goal events (simulate multiple scorers, teams, jersey numbers)
        scenario_goal_events(
            lcd,
            leds,
            delay_ctrl,
            events=[
                {
                    "home_abbr": "MTL",
                    "away_abbr": "WSH",
                    "home_score": 0,
                    "away_score": 1,
                    "scorer": {"fullName": "Alex Ovechkin", "team": "WSH", "number": 8},
                },
                {
                    "home_abbr": "MTL",
                    "away_abbr": "WSH",
                    "home_score": 1,
                    "away_score": 1,
                    "scorer": {"fullName": "Cole Caufield", "team": "MTL", "number": 22},
                },
                {
                    "home_abbr": "MTL",
                    "away_abbr": "WSH",
                    "home_score": 2,
                    "away_score": 1,
                    "scorer": {"fullName": "Nick Suzuki", "team": "MTL", "number": 14},
                },
            ],
        )

        # 4) LED smoke tests
        scenario_led_smoke_tests(lcd, leds, delay_ctrl)

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
