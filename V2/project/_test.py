#!/usr/bin/env python3
import time

from led_controller import LedController


def main():
    leds = LedController()

    # Pick any colors you want to test (RGB tuples)
    fg = (255, 0, 0)      # team color
    bg = (0, 0, 255)      # accent color

    try:
        print("Running backlight goal_animation_combo for 10 seconds... Ctrl+C to stop.")
        leds.backlight.goal_animation_combo(team=fg, accent=bg, duration=10.0)

        # Optional: small hold after animation finishes
        time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        leds.turn_off()


if __name__ == "__main__":
    main()
