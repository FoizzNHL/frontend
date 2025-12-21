#!/usr/bin/env python3
import time

from led_controller import LedController


def main():
    print("Initializing LED controller...")
    leds = LedController()

    try:
        print("Displaying number 42 on matrix")
        leds.show_number(
            42,
            fg=(255, 0, 0),     # red number
            bg=(0, 0, 20),      # dark blue background
        )

        print("Number displayed. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    finally:
        print("Turning LEDs off.")
        leds.turn_off()


if __name__ == "__main__":
    main()
