# matrix_number.py
from rpi_ws281x import PixelStrip, Color

# ------------ DIGITS (6x10 here) ------------
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

def _to_color(c):
    """Accepts either rpi_ws281x.Color or (r,g,b) tuple/list."""
    if isinstance(c, int):
        # already a packed Color(...) int
        return c
    r, g, b = c
    return Color(int(r), int(g), int(b))

def _digit_size(digits_map):
    any_digit = next(iter(digits_map.values()))
    h = len(any_digit)
    w = len(any_digit[0]) if h else 0
    return w, h

class MatrixNumberDisplay:
    """
    One instance = one LED matrix wiring/layout config.
    Call .show_number(n, fg=(r,g,b), bg=(r,g,b)).
    """
    def __init__(
        self,
        matrix_width=15,
        matrix_height=12,
        led_pin=18,
        led_freq_hz=800000,
        led_dma=10,
        led_brightness=80,
        led_invert=False,
        led_channel=0,
        serpentine=True,
        digits_map=DIGITS_6x9,
    ):
        self.w = matrix_width
        self.h = matrix_height
        self.serpentine = serpentine
        self.digits = digits_map

        self.led_count = self.w * self.h
        self.strip = PixelStrip(
            self.led_count,
            led_pin,
            led_freq_hz,
            led_dma,
            led_invert,
            led_brightness,
            led_channel,
        )
        self.strip.begin()

        self.digit_w, self.digit_h = _digit_size(self.digits)

    def _xy_to_index(self, x, y):
        # (0,0) top-left
        if self.serpentine and (y % 2 == 1):
            x = self.w - 1 - x
        return y * self.w + x

    def _set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.strip.setPixelColor(self._xy_to_index(x, y), color)

    def fill(self, color):
        c = _to_color(color)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, c)
        self.strip.show()

    def clear(self):
        self.fill((0, 0, 0))

    def _draw_bitmap(self, bitmap_rows, x0, y0, fg_color):
        for y, row in enumerate(bitmap_rows):
            for x, ch in enumerate(row):
                if ch == "1":
                    self._set_pixel(x0 + x, y0 + y, fg_color)

    def show_number(self, n: int, fg=(255, 255, 255), bg=(0, 0, 30), gap=1):
        """
        Displays 0-99 centered, using 2 colors:
          - fg: number color
          - bg: background color
        """
        s = str(n)
        if not s.isdigit() or len(s) > 2:
            raise ValueError("Only supports 0-99")

        fg_c = _to_color(fg)
        bg_c = _to_color(bg)

        total_w = self.digit_w if len(s) == 1 else (self.digit_w * 2 + gap)
        total_h = self.digit_h

        x0 = (self.w - total_w) // 2
        y0 = (self.h - total_h) // 2

        # background
        self.fill(bg_c)

        # digits
        if len(s) == 1:
            self._draw_bitmap(self.digits[s], x0, y0, fg_c)
        else:
            d1, d2 = s[0], s[1]
            self._draw_bitmap(self.digits[d1], x0, y0, fg_c)
            self._draw_bitmap(self.digits[d2], x0 + self.digit_w + gap, y0, fg_c)

        self.strip.show()

# --------- Simple functional wrapper if you prefer ---------
_default_display = None

def display_number(
    n: int,
    fg=(255, 255, 255),
    bg=(0, 0, 30),
    *,
    gap=1,
    init_kwargs=None
):
    """
    Convenience function.
    First call creates a global MatrixNumberDisplay instance.
    """
    global _default_display
    if _default_display is None:
        init_kwargs = init_kwargs or {}
        _default_display = MatrixNumberDisplay(**init_kwargs)
    _default_display.show_number(n, fg=fg, bg=bg, gap=gap)
