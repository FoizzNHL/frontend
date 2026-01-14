# lcd_display.py
import threading
from RPLCD.i2c import CharLCD

import config
from log_utils import log


class LcdDisplay:
    def __init__(self):
        self._lcd = CharLCD(
            i2c_expander='PCF8574',
            address=config.LCD_I2C_ADDRESS,
            port=config.I2C_PORT,
            cols=config.LCD_COLS,
            rows=config.LCD_ROWS,
            charmap='A00',
            auto_linebreaks=False
        )
        self._lock = threading.Lock()
        self.last_line1 = ""
        self.last_line2 = ""

    def clear(self):
        with self._lock:
            self._lcd.clear()

    def show_text(self, line1: str, line2: str = ""):
        """Clear the LCD and print line1 + line2."""
        with self._lock:
            self._lcd.clear()

            # First line
            self._lcd.cursor_pos = (0, 0)
            self._lcd.write_string((line1 or "")[:config.LCD_COLS])

            # Second line (if available)
            if config.LCD_ROWS > 1:
                self._lcd.cursor_pos = (1, 0)
                self._lcd.write_string((line2 or "")[:config.LCD_COLS])

        self.last_line1 = line1
        self.last_line2 = line2

    def show_delay_only(self, delay_seconds: int):
        """
        Only update 2nd line with delay text, keep current 1st line.
        """
        line = f"Delay: {delay_seconds:>3}s"
        with self._lock:
            if config.LCD_ROWS > 1:
                self._lcd.cursor_pos = (1, 0)
                self._lcd.write_string(line.ljust(config.LCD_COLS))

    def close(self):
        # If needed later for cleanup
        log("Shutting down LCD display.")
        self.clear()
