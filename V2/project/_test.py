#!/usr/bin/env python3
import time
import config

from screen_backlight_controller import ScreenBacklightController

TEAM_COLOR = (255, 0, 0)       # MTL red
ACCENT_COLOR = (0, 120, 255)   # MTL blue


def main():
    print("Initializing Screen Backlight...")

    backlight = None
    try:
        backlight = ScreenBacklightController(
            led_count=config.LED_COUNT,
            led_pin=config.LED_PIN,
            led_channel=config.LED_CHANNEL,
            brightness=config.LED_BRIGHTNESS,
            led_freq_hz=config.LED_FREQ_HZ,
            led_dma=config.LED_DMA,
            invert=config.LED_INVERT,
        )
    except Exception as e:
        print("\n❌ Failed to init WS281x:")
        print(e)

        print("\nQuick fix hints:")
        print("- If using GPIO13, set LED_CHANNEL = 1")
        print("- If using GPIO18, set LED_CHANNEL = 0")
        print("- Common PWM pins: GPIO12/18 (channel 0), GPIO13/19 (channel 1)")
        return

    try:
        print("Backlight ON (dim white)")
        backlight.fill((40, 40, 40))
        time.sleep(1.0)

        print("Backlight OFF")
        backlight.off()
        time.sleep(0.4)

        print("🔥 GOAL ANIMATION COMBO (10s) 🔥")
        backlight.goal_animation_combo(
            team=TEAM_COLOR,
            accent=ACCENT_COLOR,
            duration=10.0,
        )

        print("Done.")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        # Always try to turn off LEDs
        try:
            if backlight:
                backlight.off()
        except Exception:
            pass


if __name__ == "__main__":
    main()
