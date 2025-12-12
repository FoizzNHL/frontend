#!/usr/bin/env python3
import time
from rpi_ws281x import PixelStrip, Color

# ================= CONFIG =================

MATRIX_WIDTH  = 15
MATRIX_HEIGHT = 12
LED_COUNT     = MATRIX_WIDTH * MATRIX_HEIGHT

LED_PIN        = 18     # GPIO 18 recommended
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 80
LED_INVERT     = False
LED_CHANNEL    = 0

COLOR_ON  = Color(255, 0, 0)   # red
COLOR_OFF = Color(0, 0, 0)

SERPENTINE = True  # set False if wired straight

# ==========================================

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

# ---------- 5x7 FONT (digits) ----------
FONT = {
    "0": [
        "01110",
        "10001",
        "10011",
        "10101",
        "11001",
        "10001",
        "01110",
    ],
    "1": [
        "00100",
        "01100",
        "00100",
        "00100",
        "00100",
        "00100",
        "01110",
    ],
    "2": [
        "01110",
        "10001",
        "00001",
        "00010",
        "00100",
        "01000",
        "11111",
    ],
    "3": [
        "11110",
        "00001",
        "00001",
        "01110",
        "00001",
        "00001",
        "11110",
    ],
    "4": [
        "00010",
        "00110",
        "01010",
        "10010",
        "11111",
        "00010",
        "00010",
    ],
    "5": [
        "11111",
        "10000",
        "10000",
        "11110",
        "00001",
        "00001",
        "11110",
    ],
    "6": [
        "01110",
        "10000",
        "10000",
        "11110",
        "10001",
        "10001",
        "01110",
    ],
    "7": [
        "11111",
        "00001",
        "00010",
        "00100",
        "01000",
        "01000",
        "01000",
    ],
    "8": [
        "01110",
        "10001",
        "10001",
        "01110",
        "10001",
        "10001",
        "01110",
    ],
    "9": [
        "01110",
        "10001",
        "10001",
        "01111",
        "00001",
        "00001",
        "01110",
    ],
}

# ---------- MATRIX HELPERS ----------

def xy_to_index(x, y):
    """
    Convert (x, y) to LED index.
    Assumes (0,0) is top-left.
    """
    if SERPENTINE and y % 2 == 1:
        x = MATRIX_WIDTH - 1 - x
    return y * MATRIX_WIDTH + x


def clear():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, COLOR_OFF)
    strip.show()


def set_pixel(x, y, color):
    if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
        idx = xy_to_index(x, y)
        strip.setPixelColor(idx, color)


# ---------- DRAW NUMBER ----------

def draw_digit(digit, color=COLOR_ON):
    clear()

    bitmap = FONT[str(digit)]
    font_w = 5
    font_h = 7

    # center the digit in the matrix
    offset_x = (MATRIX_WIDTH - font_w) // 2
    offset_y = (MATRIX_HEIGHT - font_h) // 2

    for y in range(font_h):
        for x in range(font_w):
            if bitmap[y][x] == "1":
                set_pixel(offset_x + x, offset_y + y, color)

    strip.show()


# ---------- MAIN TEST ----------

print("Matrix digit test starting...")

try:
    while True:
        for digit in range(10):
            print(f"Showing {digit}")
            draw_digit(digit)
            time.sleep(1.5)

except KeyboardInterrupt:
    print("Stopping test.")
    clear()
