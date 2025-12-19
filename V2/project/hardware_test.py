#!/usr/bin/env python3
import time

from log_utils import log
from led_controller import LedController


def safe_call(name, fn):
    try:
        return fn()
    except Exception as e:
        log(f"[{name}] ERROR: {e}")
        return None


def main():
    log("LED STRIP test started.")

    leds = LedController()

    # Ensure strip is OFF
    safe_call("leds.turn_off", lambda: leds.turn_off())
    time.sleep(1)

    try:
        # -----------------------------
        # Test 1: Single flash sequence
        # -----------------------------
        log("Running goal flash sequence")
        safe_call("goal_flash_sequence", lambda: leds.goal_flash_sequence())
        time.sleep(2)

        # -----------------------------
        # Test 2: Repeated flashes
        # -----------------------------
        log("Repeated flash test (CTRL+C to stop)")
        while True:
            safe_call("goal_flash_sequence", lambda: leds.goal_flash_sequence())
            time.sleep(1.5)

    except KeyboardInterrupt:
        log("LED STRIP test interrupted by user.")
    finally:
        safe_call("leds.turn_off", lambda: leds.turn_off())
        log("LED STRIP test finished.")


if __name__ == "__main__":
    main()
