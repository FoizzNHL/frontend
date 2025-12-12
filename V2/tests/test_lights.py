#!/usr/bin/env python3
import time
from rpi_ws281x import PixelStrip, Color

# ---------- CONFIG (adjust if needed) ----------
LED_COUNT      = 180      # number of LEDs
LED_PIN        = 18      # GPIO pin (12 or 18 are most common)
LED_CHANNEL    = 0
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 128     # start lower to protect eyes
LED_INVERT     = False
# ---------------------------------------------

strip = PixelStrip(
    LED_COUNT,
    LED_PIN,
    LED_FREQ_HZ,
    LED_DMA,
    LED_INVERT,
    LED_BRIGHTNESS,
    LED_CHANNEL
)

strip.begin()

def fill(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

print("LED test starting...")

try:
    while True:
        print("RED")
        fill(Color(255, 0, 0))
        time.sleep(1)

        print("GREEN")
        fill(Color(0, 255, 0))
        time.sleep(1)

        print("BLUE")
        fill(Color(0, 0, 255))
        time.sleep(1)

        print("WHITE")
        fill(Color(255, 255, 255))
        time.sleep(1)

        print("OFF")
        fill(Color(0, 0, 0))
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping test, turning LEDs off.")
    fill(Color(0, 0, 0))
