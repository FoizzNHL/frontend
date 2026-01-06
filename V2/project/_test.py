#!/usr/bin/env python3
import argparse
import time

import config
from log_utils import log
from lcd_display import LcdDisplay
from led_controller import LedController
from nhl_team_colors import get_team_colors


def run_goal(leds: LedController, lcd: LcdDisplay, team: str, jersey: int):
    team = (team or "").upper()
    fg, bg = get_team_colors(team)

    log(f"TEST GOAL: team={team}, jersey={jersey}")
    lcd.show_text("TEST GOAL!!!", f"{team} #{jersey}")

    # This should call your matrix animation
    leds.goal_matrix_animation(jersey, fg=fg, bg=bg)

    lcd.show_text("TEST GOAL!!!", "DONE")
    time.sleep(1)


def run_emoji(leds: LedController, lcd: LcdDisplay, team: str, emoji: str, pulses: int):
    team = (team or "").upper()
    fg, bg = get_team_colors(team)

    log(f"TEST EMOJI: emoji={emoji}, team={team}, pulses={pulses}")
    lcd.show_text("TEST EMOJI", f"{emoji}")

    leds.matrix.emoji_animation(emoji, fg=fg, bg=bg, pulses=pulses)

    lcd.show_text("TEST EMOJI", "DONE")
    time.sleep(1)


def run_sequence(leds: LedController, lcd: LcdDisplay, team: str, jersey: int):
    """
    A quick end-to-end sequence similar to real flow:
    - happy at game start
    - goal animation
    - scheduled emoji after 20s (shortened to 3s for testing)
    - opponent goal sad emoji
    """
    team = (team or "").upper()
    fg, bg = get_team_colors(team)

    log("Running test SEQUENCE...")
    lcd.show_text("SEQUENCE", "start")

    # Game start emoji
    leds.matrix.emoji_animation("happy", fg=fg, bg=bg, pulses=4)
    time.sleep(0.5)

    # Goal jersey animation
    lcd.show_text("GOAL!!!", f"{team} #{jersey}")
    leds.goal_matrix_animation(jersey, fg=fg, bg=bg)

    # "Scheduled" emoji (shorter delay than 20s)
    lcd.show_text("WAIT", "3s -> emoji")
    time.sleep(3)
    leds.matrix.emoji_animation("happy", fg=fg, bg=bg, pulses=4)

    # Opponent goal simulation
    lcd.show_text("GOAL AGAINST", "sad")
    leds.matrix.emoji_animation("sad", fg=fg, bg=bg, pulses=4)

    lcd.show_text("SEQUENCE", "done")
    time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="Test LED matrix goal + emoji animations (no backend needed).")
    parser.add_argument("--mode", choices=["goal", "emoji", "sequence"], default="sequence")
    parser.add_argument("--team", default=getattr(config, "TEAM_ABBR", "MTL"), help="Team abbr for colors (ex: MTL, BOS)")
    parser.add_argument("--jersey", type=int, default=22, help="Jersey number to display (0-99)")
    parser.add_argument("--emoji", default="happy", choices=["happy", "sad", "stressed"], help="Emoji name")
    parser.add_argument("--pulses", type=int, default=4, help="Emoji pulses")
    args = parser.parse_args()

    lcd = LcdDisplay()
    leds = LedController()

    try:
        lcd.show_text("ANIM TEST", args.mode)
        time.sleep(0.5)

        if args.mode == "goal":
            run_goal(leds, lcd, args.team, args.jersey)
        elif args.mode == "emoji":
            run_emoji(leds, lcd, args.team, args.emoji, args.pulses)
        else:
            run_sequence(leds, lcd, args.team, args.jersey)

    except KeyboardInterrupt:
        log("Animation test interrupted by user.")
    except Exception as e:
        log(f"ERROR in test script: {e}")
        try:
            lcd.show_text("TEST ERROR", str(e)[:getattr(config, "LCD_COLS", 16)])
        except Exception:
            pass
    finally:
        try:
            lcd.clear()
            lcd.close()
        except Exception:
            pass
        try:
            leds.turn_off()
        except Exception:
            pass


if __name__ == "__main__":
    main()
