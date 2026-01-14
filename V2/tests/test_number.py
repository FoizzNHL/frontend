#!/usr/bin/env python3
import time
from rpi_ws281x import PixelStrip, Color

# ================= MATRIX / STRIP CONFIG =================
MATRIX_WIDTH  = 15
MATRIX_HEIGHT = 12
LED_COUNT     = MATRIX_WIDTH * MATRIX_HEIGHT

LED_PIN        = 18       # try 12 or 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 80
LED_INVERT     = False
LED_CHANNEL    = 0

SERPENTINE = True         # most common on LED matrices
# =========================================================

# ------------ COLORS ------------
FG = Color(255, 255, 255)   # number color (white)
BG = Color(0, 0, 30)        # background color (dim blue)
# -------------------------------

# ------------ YOUR DIGITS ------------
DIGITS_6x9 = {
    "0":["111111","110011","110011","110011","110011","110011","110011","110011","111111","111111"],
    "1":["001100","011100","001100","001100","001100","001100","001100","001100","111111","111111"],
    "2":["111111","111111","000011","000011","111111","111111","110000","110000","111111","111111"],
    "3":["111111","111111","000011","000011","001111","001111","000011","000011","111111","111111"],
    "4":["110011","110011","110011","110011","111111","111111","000011","000011","000011","000011"],
    "5":["111111","111111","110000","110000","111111","111111","000011","000011","111111","111111"],
    "6":["111111","111111","110000","110000","111111","111111","110011","110011","111111","111111"],
    "7":["111111","111111","000011","000110","001100","001100","011000","011000","011000","011000"],
    "8":["111111","110011","110011","110011","111111","111111","110011","110011","110011","111111"],
    "9":["111111","110011","110011","110011","111111","111111","000011","000011","111111","111111"]
}
# -----------------------------------

strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
    LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

def xy_to_index(x, y):
    # (0,0) = top-left
    if SERPENTINE and (y % 2 == 1):
        x = MATRIX_WIDTH - 1 - x
    return y * MATRIX_WIDTH + x

def fill_all(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def set_pixel(x, y, color):
    if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
        strip.setPixelColor(xy_to_index(x, y), color)

def draw_bitmap(bitmap_rows, x0, y0, fg_color):
    for y, row in enumerate(bitmap_rows):
        for x, ch in enumerate(row):
            if ch == "1":
                set_pixel(x0 + x, y0 + y, fg_color)

def get_digit_size():
    any_digit = next(iter(DIGITS_6x9.values()))
    h = len(any_digit)
    w = len(any_digit[0]) if h else 0
    return w, h

def draw_number(n: int, fg_color=FG, bg_color=BG, gap=1):
    s = str(n)
    if not s.isdigit() or len(s) > 2:
        raise ValueError("Only supports 0-99")

    digit_w, digit_h = get_digit_size()
    total_w = digit_w if len(s) == 1 else (digit_w * 2 + gap)
    total_h = digit_h

    x0 = (MATRIX_WIDTH  - total_w) // 2
    y0 = (MATRIX_HEIGHT - total_h) // 2

    # 1) background fill
    fill_all(bg_color)

    # 2) draw digits over it
    if len(s) == 1:
        draw_bitmap(DIGITS_6x9[s], x0, y0, fg_color)
    else:
        d1, d2 = s[0], s[1]
        draw_bitmap(DIGITS_6x9[d1], x0, y0, fg_color)
        draw_bitmap(DIGITS_6x9[d2], x0 + digit_w + gap, y0, fg_color)

    strip.show()

if __name__ == "__main__":
    print("2-color matrix number test (Ctrl+C to stop)")
    try:
        players = [13, 14, 22, 27, 40, 73, 88, 8, 9, 0]
        while True:
            for p in players:
                print("Showing:", p)
                draw_number(p, fg_color=FG, bg_color=BG, gap=1)
                time.sleep(1.5)

                # quick invert test (swap fg/bg)
                draw_number(p, fg_color=BG, bg_color=FG, gap=1)
                time.sleep(0.7)

    except KeyboardInterrupt:
        print("Stopping, clearing...")
        fill_all(Color(0, 0, 0))
