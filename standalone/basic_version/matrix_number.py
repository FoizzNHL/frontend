# matrix_number.py
from rpi_ws281x import PixelStrip, Color
import time
import random


# ------------ DIGITS (6x10) ------------
# (Name kept for backward-compat, but these are 6 wide x 10 tall)
DIGITS_6x9 = {
    "0": ["111111", "110011", "110011", "110011", "110011", "110011", "110011", "110011", "111111", "111111"],
    "1": ["001100", "011100", "001100", "001100", "001100", "001100", "001100", "001100", "111111", "111111"],
    "2": ["111111", "111111", "000011", "000011", "111111", "111111", "110000", "110000", "111111", "111111"],
    "3": ["111111", "111111", "000011", "000011", "001111", "001111", "000011", "000011", "111111", "111111"],
    "4": ["110011", "110011", "110011", "110011", "111111", "111111", "000011", "000011", "000011", "000011"],
    "5": ["111111", "111111", "110000", "110000", "111111", "111111", "000011", "000011", "111111", "111111"],
    "6": ["111111", "111111", "110000", "110000", "111111", "111111", "110011", "110011", "111111", "111111"],
    "7": ["111111", "111111", "000011", "000110", "001100", "001100", "011000", "011000", "011000", "011000"],
    "8": ["111111", "110011", "110011", "110011", "111111", "111111", "110011", "110011", "110011", "111111"],
    "9": ["111111", "110011", "110011", "110011", "111111", "111111", "000011", "000011", "111111", "111111"],
}

# ------------ EMOJIS (14x12) ------------
# (Your strings are already width=14, height=12)
EMOJIS_14x12 = {
    "sad": [
        "00000000000000",
        "00000000000000",
        "00111000011100",
        "00111000011100",
        "00111000011100",
        "00000000000000",
        "00000000000000",
        "00011111111000",
        "00111111111100",
        "01111111111110",
        "00000000000000",
        "00000000000000",
    ],
    "happy": [
        "00000000000000",
        "00000000000000",
        "00111000011100",
        "00111000011100",
        "00111000011100",
        "00000000000000",
        "00000000000000",
        "01111111111110",
        "00111111111100",
        "00011111111000",
        "00000000000000",
        "00000000000000",
    ],
    "stressed": [
        "00000000000000",
        "00000000000000",
        "00111000011100",
        "00111000011100",
        "00111000011100",
        "00000000000000",
        "00000000000000",
        "10001000100010",
        "01010101010100",
        "00100010001000",
        "00000000000000",
        "00000000000000",
    ],
}


def _clamp(v):
    return 0 if v < 0 else (255 if v > 255 else v)


def _dim(rgb, factor: float):
    r, g, b = rgb
    return (_clamp(int(r * factor)), _clamp(int(g * factor)), _clamp(int(b * factor)))


def _to_color(c):
    """Accepts either rpi_ws281x.Color (int) or (r,g,b) tuple/list."""
    if isinstance(c, int):
        return c
    r, g, b = c
    return Color(int(r), int(g), int(b))


def _digit_size(digits_map):
    any_digit = next(iter(digits_map.values()))
    h = len(any_digit)
    w = len(any_digit[0]) if h else 0
    return w, h


def _validate_bitmap(bitmap_rows, expected_w=None, expected_h=None, name="bitmap"):
    if not bitmap_rows:
        raise ValueError(f"{name} is empty")

    h = len(bitmap_rows)
    w = len(bitmap_rows[0])

    for i, row in enumerate(bitmap_rows):
        if len(row) != w:
            raise ValueError(f"{name} row {i} has width {len(row)} but expected {w}")
        for ch in row:
            if ch not in ("0", "1"):
                raise ValueError(f"{name} contains invalid char '{ch}' (only '0'/'1')")

    if expected_w is not None and w != expected_w:
        raise ValueError(f"{name} width is {w} but expected {expected_w}")
    if expected_h is not None and h != expected_h:
        raise ValueError(f"{name} height is {h} but expected {expected_h}")

    return w, h


class MatrixNumberDisplay:
    """
    14x12 matrix number + emoji display.

    NOTE:
    - Defaults are set for a 14(w) x 12(h) matrix.
    - Digits are 6x10, centered.
    - Two-digit numbers fit if gap <= 2 (gap=1 default).
    """

    def __init__(
        self,
        matrix_width=14,
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
        self.w = int(matrix_width)
        self.h = int(matrix_height)
        self.serpentine = serpentine
        self.digits = digits_map

        # Validate digits once
        self.digit_w, self.digit_h = _digit_size(self.digits)
        for k, bmp in self.digits.items():
            _validate_bitmap(bmp, expected_w=self.digit_w, expected_h=self.digit_h, name=f"digit '{k}'")

        # Validate emojis once (expected 14x12)
        for k, bmp in EMOJIS_14x12.items():
            _validate_bitmap(bmp, expected_w=14, expected_h=12, name=f"emoji '{k}'")

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

    def _xy_to_index(self, x, y):
        # rotate display 180°
        x = self.w - 1 - x
        y = self.h - 1 - y

        # serpentine mapping based on the (rotated) row
        if self.serpentine and (y % 2 == 1):
            x = self.w - 1 - x

        return y * self.w + x

    def _set_pixel(self, x, y, color_int):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.strip.setPixelColor(self._xy_to_index(x, y), color_int)

    def fill(self, color):
        c = _to_color(color)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, c)
        self.strip.show()

    def clear(self):
        self.fill((0, 0, 0))

    def _draw_bitmap(self, bitmap_rows, x0, y0, fg_color_int):
        for y, row in enumerate(bitmap_rows):
            for x, ch in enumerate(row):
                if ch == "1":
                    self._set_pixel(x0 + x, y0 + y, fg_color_int)

    def show_number(self, n: int, fg=(255, 255, 255), bg=(0, 0, 30), gap=1):
        """
        Displays 0-99 centered.
        On 14x12 with 6x10 digits:
          - gap=1 => 2 digits use width 13 (fits)
          - gap=2 => width 14 (fits)
          - gap>=3 => won't fit (raises)
        """
        s = str(n)
        if not s.isdigit() or len(s) > 2:
            raise ValueError("Only supports 0-99")

        fg_c = _to_color(fg)
        bg_c = _to_color(bg)

        total_w = self.digit_w if len(s) == 1 else (self.digit_w * 2 + gap)
        total_h = self.digit_h

        if total_w > self.w or total_h > self.h:
            raise ValueError(
                f"Number bitmap ({total_w}x{total_h}) won't fit matrix ({self.w}x{self.h}). "
                f"Try smaller gap (<=2) or smaller digits."
            )

        x0 = (self.w - total_w) // 2
        y0 = (self.h - total_h) // 2

        self.fill(bg_c)

        if len(s) == 1:
            self._draw_bitmap(self.digits[s], x0, y0, fg_c)
        else:
            d1, d2 = s[0], s[1]
            self._draw_bitmap(self.digits[d1], x0, y0, fg_c)
            self._draw_bitmap(self.digits[d2], x0 + self.digit_w + gap, y0, fg_c)

        self.strip.show()

    def _fill_no_show(self, color_int):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color_int)

    def _set_pixel_no_bounds(self, x, y, color_int):
        self.strip.setPixelColor(self._xy_to_index(x, y), color_int)

    def _wipe_bg(self, bg_color, direction="lr", step_delay=0.01):
        bg_c = _to_color(bg_color)

        if direction == "lr":
            for x in range(self.w):
                for y in range(self.h):
                    self._set_pixel(x, y, bg_c)
                self.strip.show()
                time.sleep(step_delay)

        elif direction == "tb":
            for y in range(self.h):
                for x in range(self.w):
                    self._set_pixel(x, y, bg_c)
                self.strip.show()
                time.sleep(step_delay)

    def _draw_number_at(self, n: int, x0: int, y0: int, fg_color, gap=1):
        s = str(n)
        if not s.isdigit() or len(s) > 2:
            return

        fg_c = _to_color(fg_color)

        total_w = self.digit_w if len(s) == 1 else (self.digit_w * 2 + gap)
        total_h = self.digit_h
        if (x0 < 0) or (y0 < 0) or (x0 + total_w > self.w) or (y0 + total_h > self.h):
            return  # silently skip if it wouldn't fit

        if len(s) == 1:
            self._draw_bitmap(self.digits[s], x0, y0, fg_c)
        else:
            d1, d2 = s[0], s[1]
            self._draw_bitmap(self.digits[d1], x0, y0, fg_c)
            self._draw_bitmap(self.digits[d2], x0 + self.digit_w + gap, y0, fg_c)

    def goal_number_animation(self, n: int, fg, bg, gap=1):
        """
        Extended GOAL animation (longer & more hype):
        1) Slow background wipe
        2) Big pop + bounce
        3) Extended sparkle/confetti
        4) Pulse hold
        5) Invert flashes
        6) Final steady display
        """
        s = str(n)
        if not s.isdigit() or len(s) > 2:
            raise ValueError("Only supports 0-99")

        total_w = self.digit_w if len(s) == 1 else (self.digit_w * 2 + gap)
        total_h = self.digit_h

        if total_w > self.w or total_h > self.h:
            raise ValueError(
                f"Number bitmap ({total_w}x{total_h}) won't fit matrix ({self.w}x{self.h}). "
                f"Try gap<=2."
            )

        cx = (self.w - total_w) // 2
        cy = (self.h - total_h) // 2

        def dim(rgb, factor):
            return (
                max(0, min(255, int(rgb[0] * factor))),
                max(0, min(255, int(rgb[1] * factor))),
                max(0, min(255, int(rgb[2] * factor))),
            )

        # 1) Slow background wipe
        bg_int = _to_color(bg)
        for x in range(self.w):
            for y in range(self.h):
                self._set_pixel(x, y, bg_int)
            self.strip.show()
            time.sleep(0.02)

        # 2) Big pop / bounce
        # (tuned for 12px height: keep y offsets within [-? .. +?] so it doesn't clip)
        bounce_frames = [
            (0, 2, 0.35),
            (0, 1, 0.55),
            (0, 0, 0.75),
            (0, 0, 1.00),  # impact
            (1, 0, 1.00),
            (-1, 0, 1.00),
            (0, 0, 1.00),
            (0, 1, 0.85),
            (0, 0, 1.00),
            (0, 1, 0.90),
            (0, 0, 1.00),
        ]

        for dx, dy, bright in bounce_frames:
            self.fill(bg)
            self._draw_number_at(n, cx + dx, cy + dy, dim(fg, bright), gap)
            self.strip.show()
            time.sleep(0.08)

        # 3) Extended sparkles / confetti
        fg_int = _to_color(fg)
        alt_int = _to_color(dim(fg, 0.35))

        for _ in range(24):
            self.fill(bg)
            self._draw_number_at(n, cx, cy, fg, gap)

            for __ in range(30):
                x = random.randint(0, self.w - 1)
                y = random.randint(0, self.h - 1)
                self._set_pixel(x, y, fg_int if random.random() > 0.4 else alt_int)

            self.strip.show()
            time.sleep(0.07)

        # 4) Pulse hold
        for pulse in [0.85, 1.0, 0.9, 1.0, 0.95, 1.0]:
            self.fill(bg)
            self._draw_number_at(n, cx, cy, dim(fg, pulse), gap)
            self.strip.show()
            time.sleep(0.18)

        # 5) Invert flashes
        for _ in range(3):
            self.show_number(n, fg=bg, bg=fg, gap=gap)
            time.sleep(0.15)
            self.show_number(n, fg=fg, bg=bg, gap=gap)
            time.sleep(0.15)

        # 6) Final hold
        self.show_number(n, fg=fg, bg=bg, gap=gap)
        time.sleep(1.2)

    def show_emoji(self, name: str, fg, bg=(0, 0, 0)):
        """
        Draw 14x12 emoji on the matrix.
        Since the matrix is 14x12 and emojis are 14x12, we draw at (0,0).
        """
        if name not in EMOJIS_14x12:
            raise ValueError(f"Unknown emoji: {name}")

        bitmap = EMOJIS_14x12[name]

        # background
        self.fill(bg)

        fg_int = _to_color(fg)
        for y, row in enumerate(bitmap):
            for x, ch in enumerate(row):
                if ch == "1":
                    self._set_pixel(x, y, fg_int)

        self.strip.show()

    def emoji_animation(self, name: str, fg, bg, pulses: int = 4):
        """
        Small 'breathing' animation for emojis.
        """

        def dim(rgb, f):
            return (
                max(0, min(255, int(rgb[0] * f))),
                max(0, min(255, int(rgb[1] * f))),
                max(0, min(255, int(rgb[2] * f))),
            )

        for _ in range(pulses):
            self.show_emoji(name, fg=dim(fg, 0.65), bg=bg)
            time.sleep(0.20)
            self.show_emoji(name, fg=dim(fg, 1.00), bg=bg)
            time.sleep(0.20)

        self.show_emoji(name, fg=fg, bg=bg)


# --------- Simple functional wrapper if you prefer ---------
_default_display = None


def display_number(
    n: int,
    fg=(255, 255, 255),
    bg=(0, 0, 30),
    *,
    gap=1,
    init_kwargs=None,
):
    """
    Convenience function.
    First call creates a global MatrixNumberDisplay instance (defaults 14x12).
    """
    global _default_display
    if _default_display is None:
        init_kwargs = init_kwargs or {}
        # Ensure 14x12 defaults unless caller overrides
        init_kwargs.setdefault("matrix_width", 14)
        init_kwargs.setdefault("matrix_height", 12)
        _default_display = MatrixNumberDisplay(**init_kwargs)

    _default_display.show_number(n, fg=fg, bg=bg, gap=gap)
