# button_controller.py
import time
from threading import Thread

from gpiozero import Button

import config
from log_utils import log


class DelayController:
    def __init__(self, lcd_display):
        self.lcd = lcd_display
        self.delay_seconds = config.DEFAULT_DELAY_SECONDS

        self._press_start_time = None
        self._is_holding = False

        # IMPORTANT:
        # active_state=False inverts the logic so "pressed" triggers when the input goes LOW->HIGH (or vice versa)
        # For an NC button ("always on unless pressed"), this usually makes callbacks match real presses.
        self.button = Button(
            config.BUTTON_PIN,
            pull_up=True,
            active_state=False,   # ✅ invert logic for NC button
            bounce_time=0.05
        )

        self.button.when_pressed = self._on_pressed
        self.button.when_released = self._on_released

    # ---------- Public ----------
    def get_delay(self) -> int:
        return self.delay_seconds

    # ---------- Internal helpers ----------
    def _hold_worker(self):
        time.sleep(config.HOLD_THRESHOLD)

        if not self._is_holding:
            return

        log("Hold detected → decreasing delay continuously")
        while self._is_holding and self.delay_seconds > 0:
            self.delay_seconds -= 1
            log(f"Delay updated (hold): {self.delay_seconds}s")
            self.lcd.show_delay_only(self.delay_seconds)
            time.sleep(config.DECREMENT_DELAY)

    def _on_pressed(self):
        self._press_start_time = time.time()
        self._is_holding = True
        log("Button pressed.")

        Thread(target=self._hold_worker, daemon=True).start()

    def _on_released(self):
        self._is_holding = False
        if self._press_start_time is None:
            return

        press_duration = time.time() - self._press_start_time

        if press_duration < config.HOLD_THRESHOLD:
            self.delay_seconds += 1
            log(f"Quick tap detected → Delay incremented to {self.delay_seconds}s")
            self.lcd.show_delay_only(self.delay_seconds)
        else:
            log("Button released after hold.")
