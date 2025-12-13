# screen_backlight_controller.py
from rpi_ws281x import PixelStrip, Color

def _to_color(rgb):
    if isinstance(rgb, int):
        return rgb
    r, g, b = rgb
    return Color(int(r), int(g), int(b))

class ScreenBacklightController:
    def __init__(
        self,
        led_count: int,
        led_pin: int,
        led_channel: int = 0,
        brightness: int = 128,
        led_freq_hz: int = 800000,
        led_dma: int = 10,
        invert: bool = False,
    ):
        self.strip = PixelStrip(
            led_count, led_pin, led_freq_hz, led_dma, invert, brightness, led_channel
        )
        self.strip.begin()

    def fill(self, color):
        c = _to_color(color)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, c)
        self.strip.show()

    def off(self):
        self.fill((0, 0, 0))

    def goal_flash(self, flashes=6, on=(255, 255, 255), off=(0, 0, 0), delay=0.12):
        import time
        for _ in range(flashes):
            self.fill(on)
            time.sleep(delay)
            self.fill(off)
            time.sleep(delay)
