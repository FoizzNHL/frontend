#!/usr/bin/env python3
import time
import config

from screen_backlight_controller import ScreenBacklightController

# ----------------------------
# TEAM COLORS (MTL)
# ----------------------------
TEAM_COLOR = (255, 0, 0)       # Canadiens red
ACCENT_COLOR = (0, 120, 255)   # Canadiens blue


def main():
    print("Initializing Screen Backlight...")

    backlight = ScreenBacklightController(
        led_count=config.LED_COUNT,
        led_pin=config.LED_PIN,
        led_channel=config.LED_CHANNEL,
        brightness=config.LED_BRIGHTNESS,
        led_freq_hz=config.LED_FREQ_HZ,
        led_dma=config.LED_DMA,
        invert=config.LED_INVERT,
    )

    try:
        # Small pre-test so you know wiring works
        print("Backlight ON (dim white)")
        backlight.fill((40, 40, 40))
        time.sleep(1.5)

        print("Backlight OFF")
        backlight.off()
        time.sleep(0.5)

        print("🔥 GOAL ANIMATION TEST 🔥")
        backlight.goal_animation_combo(
            team=TEAM_COLOR,
            accent=ACCENT_COLOR,
            duration=10.0,
        )

        print("Animation finished.")
        backlight.off()

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        backlight.off()


if __name__ == "__main__":
    main()
