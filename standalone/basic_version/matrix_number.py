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
# These are exactly width=14, height=12 (perfect for your 14x12 matrix)
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
    14x12 matrix number + emoji display for a DIY serpentine-wired strip grid.

    You said your entry (LED index 0) is BOTTOM-RIGHT.

    The ONLY remaining "everything looks random" cause is the mapping assumptions.
    So we expose 2 knobs that matter for DIY grids:

      serpentine_axis:
        - "rows" => you ran the strip along rows (horizontal runs)
        - "cols" => you ran the strip along columns (vertical runs)

      first_dir:
        - if serpentine_axis="rows": "left" or "right" (direction of the first run from the start corner)
        - if serpentine_axis="cols": "up" or "down" (direction of the first run from the start corner)

    Defaults are the most common for bottom-right start: rows + first run goes LEFT.
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
        start_corner="bottom_right",   # top_left/top_right/bottom_left/bottom_right
        serpentine_axis="rows",        # rows or cols
        first_dir="left",              # rows: left/right, cols: up/down
        digits_map=DIGITS_6x9,
    ):
        self.w = int(matrix_width)
        self.h = int(matrix_height)

        self.serpentine = bool(serpentine)
        self.start_corner = start_corner
        self.serpentine_axis = serpentine_axis
        self.first_dir = first_dir

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

    # ---------------- Mapping ----------------

    def _xy_to_index(self, x, y):
        """
        Maps (x,y) where:
          x: 0..w-1 left->right
          y: 0..h-1 top->bottom

        start_corner: where LED index 0 physically is
        serpentine_axis: "rows" or "cols"
        first_dir: direction of the first run from the start corner
        """

        # Remap so that the "origin-space" (ox,oy) has (0,0) at start_corner
        if self.start_corner == "top_left":
            ox, oy = x, y
        elif self.start_corner == "top_right":
            ox, oy = (self.w - 1 - x), y
        elif self.start_corner == "bottom_left":
            ox, oy = x, (self.h - 1 - y)
        elif self.start_corner == "bottom_right":
            ox, oy = (self.w - 1 - x), (self.h - 1 - y)
        else:
            raise ValueError("start_corner must be top_left/top_right/bottom_left/bottom_right")

        if not self.serpentine:
            # simple raster in origin-space (row-major)
            return oy * self.w + ox

        if self.serpentine_axis == "rows":
            row = oy

            # row 0 direction
            forward = (self.first_dir == "right")  # True => ox increases along row
            if (row % 2) == 1:
                forward = not forward

            col = ox if forward else (self.w - 1 - ox)
            return row * self.w + col

        if self.serpentine_axis == "cols":
            col = ox

            # col 0 direction
            forward = (self.first_dir == "down")  # True => oy increases down the column
            if (col % 2) == 1:
                forward = not forward

            row = oy if forward else (self.h - 1 - oy)
            return col * self.h + row

        raise ValueError("serpentine_axis must be 'rows' or 'cols'")

    # ---------------- Pixels ----------------

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

    # ---------------- Numbers ----------------

    def show_number(self, n: int, fg=(255, 255, 255), bg=(0, 0, 30), gap=1):
        """
        Displays 0-99 centered.
        On 14x12 with 6x10 digits:
          - gap=1 => 2 digits width 13 (fits)
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
                f"Try gap<=2."
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
            return

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
                f"Number bitmap ({total_w}x{total_h}) won't fit matrix ({self.w}x{self.h}). Try gap<=2."
            )

        cx = (self.w - total_w) // 2
        cy = (self.h - total_h) // 2

        def dim(rgb, factor):
            return (
                max(0, min(255, int(rgb[0] * factor))),
                max(0, min(255, int(rgb[1] * factor))),
                max(0, min(255, int(rgb[2] * factor))),
            )

        # 1) SLOW BACKGROUND WIPE
        bg_int = _to_color(bg)
        for x in range(self.w):
            for y in range(self.h):
                self._set_pixel(x, y, bg_int)
            self.strip.show()
            time.sleep(0.02)

        # 2) POP / BOUNCE (tuned for 12px height)
        bounce_frames = [
            (0, 2, 0.35),
            (0, 1, 0.55),
            (0, 0, 0.75),
            (0, 0, 1.00),
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

        # 3) SPARKLES / CONFETTI
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

        # 4) PULSE HOLD
        for pulse in [0.85, 1.0, 0.9, 1.0, 0.95, 1.0]:
            self.fill(bg)
            self._draw_number_at(n, cx, cy, dim(fg, pulse), gap)
            self.strip.show()
            time.sleep(0.18)

        # 5) INVERT FLASHES
        for _ in range(3):
            self.show_number(n, fg=bg, bg=fg, gap=gap)
            time.sleep(0.15)
            self.show_number(n, fg=fg, bg=bg, gap=gap)
            time.sleep(0.15)

        # 6) FINAL HOLD
        self.show_number(n, fg=fg, bg=bg, gap=gap)
        time.sleep(1.2)

    # ---------------- Emojis ----------------

    def show_emoji(self, name: str, fg, bg=(0, 0, 0)):
        """
        Draw 14x12 emoji covering the whole matrix (no centering needed).
        """
        if name not in EMOJIS_14x12:
            raise ValueError(f"Unknown emoji: {name}")

        bitmap = EMOJIS_14x12[name]
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

    # ---------------- Debug helpers ----------------

    def debug_corners(self):
        """
        Lights 4 corners with distinct colors to verify orientation:
          TL = Red, TR = Green, BL = Blue, BR = White
        """
        self.clear()
        self._set_pixel(0, 0, _to_color((255, 0, 0)))
        self._set_pixel(self.w - 1, 0, _to_color((0, 255, 0)))
        self._set_pixel(0, self.h - 1, _to_color((0, 0, 255)))
        self._set_pixel(self.w - 1, self.h - 1, _to_color((255, 255, 255)))
        self.strip.show()

    def scan(self, delay=0.05):
        """
        Scans in draw-coordinate order (x then y).
        If mapping matches your soldering, the dot will move nicely cell-to-cell.
        """
        for y in range(self.h):
            for x in range(self.w):
                self.clear()
                self._set_pixel(x, y, _to_color((255, 255, 255)))
                self.strip.show()
                time.sleep(delay)

    def index_chase(self, delay=0.03):
        """
        Lights LEDs by raw index (0..N-1). Useful to see physical wiring path.
        """
        for i in range(self.led_count):
            self.clear()
            self.strip.setPixelColor(i, _to_color((255, 255, 255)))
            self.strip.show()
            time.sleep(delay)


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
    First call creates a global MatrixNumberDisplay instance.

    Defaults assume:
      - 14x12
      - start_corner = bottom_right
      - serpentine_axis = rows
      - first_dir = left

    If your scan looks wrong, change init_kwargs like:
      init_kwargs={"serpentine_axis":"cols","first_dir":"up"}
    """
    global _default_display
    if _default_display is None:
        init_kwargs = init_kwargs or {}
        init_kwargs.setdefault("matrix_width", 14)
        init_kwargs.setdefault("matrix_height", 12)
        init_kwargs.setdefault("start_corner", "bottom_right")
        init_kwargs.setdefault("serpentine_axis", "rows")
        init_kwargs.setdefault("first_dir", "left")
        _default_display = MatrixNumberDisplay(**init_kwargs)

    _default_display.show_number(n, fg=fg, bg=bg, gap=gap)
