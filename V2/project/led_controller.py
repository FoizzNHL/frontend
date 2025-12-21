# led_controller.py
from matrix_number import MatrixNumberDisplay
from screen_backlight_controller import ScreenBacklightController
import config

class LedController:
    def __init__(self):
        # A) Score matrix (15x12 on GPIO 18 for example)
        self.matrix = MatrixNumberDisplay(
            matrix_width=15,
            matrix_height=12,
            led_pin=18,
            led_channel=0,     # channel 0
            led_brightness=80,
            serpentine=True,
        )

        # B) Back-of-screen strip (example: 60 LEDs on GPIO 13 channel 1)
        self.backlight = ScreenBacklightController(
            led_count=config.LED_COUNT,
            led_pin=config.LED_PIN,
            led_channel=1,     # channel 1 (important if using 13/18 combo)
            brightness=config.LED_BRIGHTNESS,
        )

    # ---- Number display API ----
    def show_number(self, n: int, fg=(255,255,255), bg=(0,0,30)):
        self.matrix.show_number(n, fg=fg, bg=bg)

    # ---- Backlight API ----
    def set_backlight(self, color):
        self.backlight.fill(color)

    def goal_flash_sequence(self):
        # flash backlight + show score on matrix (example)
        self.backlight.goal_flash(flashes=8, on=(255,255,255), delay=0.10)

    def turn_off(self):
        self.matrix.clear()
        self.backlight.off()

    def goal_matrix_animation(self, n, fg, bg):
        self.matrix.goal_number_animation(n, fg=fg, bg=bg)
        self.backlight.goal_flash(flashes=8, on=(255,255,255), delay=0.10)
