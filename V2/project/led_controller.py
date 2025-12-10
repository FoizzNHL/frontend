# led_controller.py
import time
from rpi_ws281x import PixelStrip, Color

import config
from log_utils import log


class LedController:
    def __init__(self):
        self.strip = PixelStrip(
            config.LED_COUNT,
            config.LED_PIN,
            config.LED_FREQ_HZ,
            config.LED_DMA,
            config.LED_INVERT,
            config.LED_BRIGHTNESS,
            config.LED_CHANNEL
        )
        self.strip.begin()

        # Colors
        self.HABS_RED  = Color(255, 0, 0)
        self.HABS_BLUE = Color(0, 0, 255)
        self.WHITE     = Color(255, 255, 255)
        self.OFF_COLOR = Color(0, 0, 0)

    def fill(self, color):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def goal_flash_sequence(self, duration_seconds: int = 6):
        log("Starting LED goal animation...")
        end_time = time.time() + duration_seconds
        colors = [self.HABS_RED, self.WHITE, self.HABS_BLUE, self.WHITE]
        idx = 0

        while time.time() < end_time:
            self.fill(colors[idx])
            idx = (idx + 1) % len(colors)
            time.sleep(0.15)

        self.fill(self.OFF_COLOR)
        log("LED animation finished.")

    def turn_off(self):
        self.fill(self.OFF_COLOR)
        log("LEDs turned off.")
