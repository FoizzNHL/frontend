# button_controller.py
import time
from gpiozero import Button

import config
from log_utils import log


class DelayController:
    def __init__(self, lcd_display):
        self.lcd = lcd_display
        self.delay_seconds = config.DEFAULT_DELAY_SECONDS

        # No active_state here (your pin isn't floating, so gpiozero rejects it)
        self.button = Button(
            config.BUTTON_PIN,
            pull_up=True,
            bounce_time=0.05
        )

        # Auto-detect inversion:
        # If idle reads "pressed", your wiring behaves inverted (NC / always-on-unless-pressed).
        idle_is_pressed = self.button.is_pressed
        self._invert = idle_is_pressed is True

        log(f"Button init: value={self.button.value} is_pressed={idle_is_pressed} invert={self._invert}")

        self._last_phys_pressed = self._phys_pressed()
        self._press_start_time = None
        self._holding = False
        self._last_decrement_at = 0.0

    def _phys_pressed(self) -> bool:
        # We define "physical pressed" as what *you* do with your finger.
        # If the wiring is inverted, flip gpiozero's is_pressed.
        return (not self.button.is_pressed) if self._invert else self.button.is_pressed

    # ---------- Public ----------
    def get_delay(self) -> int:
        # Update state each time the app asks for delay
        self.update()
        return self.delay_seconds

    def update(self):
        now = time.time()
        pressed = self._phys_pressed()

        # Press edge
        if pressed and not self._last_phys_pressed:
            self._press_start_time = now
            self._holding = True
            self._last_decrement_at = now
            log("Button press (physical) detected")

        # While held: after threshold, decrement continuously
        if pressed and self._holding and self._press_start_time is not None:
            held_for = now - self._press_start_time
            if held_for >= config.HOLD_THRESHOLD:
                if (now - self._last_decrement_at) >= config.DECREMENT_DELAY and self.delay_seconds > 0:
                    self.delay_seconds -= 1
                    self._last_decrement_at = now
                    log(f"Delay updated (hold): {self.delay_seconds}s")
                    self.lcd.show_delay_only(self.delay_seconds)

        # Release edge
        if (not pressed) and self._last_phys_pressed:
            log("Button release (physical) detected")
            self._holding = False

            if self._press_start_time is not None:
                press_duration = now - self._press_start_time
                self._press_start_time = None

                # Quick tap => increment
                if press_duration < config.HOLD_THRESHOLD:
                    self.delay_seconds += 1
                    log(f"Quick tap => Delay incremented to {self.delay_seconds}s")
                    self.lcd.show_delay_only(self.delay_seconds)

        self._last_phys_pressed = pressed
