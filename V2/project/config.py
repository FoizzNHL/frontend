# config.py

# ---------- BACKEND ----------
BACKEND_BASE_URL = "https://api-web.nhle.com/v1"
TEAM_ABBR = "CHI"

# ---------- LCD ----------
LCD_I2C_ADDRESS = 0x27
I2C_PORT = 1
LCD_COLS = 16
LCD_ROWS = 2

# ---------- POLLING ----------
POLL_INTERVAL_SECONDS = 5

# ---------- LED STRIP ----------
LED_COUNT      = 15
LED_PIN        = 19
LED_CHANNEL    = 0
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False

# ---------- BUTTON ----------
BUTTON_PIN       = 17
DECREMENT_DELAY  = 0.2
HOLD_THRESHOLD   = 0.3

# Initial delay
DEFAULT_DELAY_SECONDS = 10
