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

    def goal_animation_police(self, team=(255, 0, 0), accent=(0, 120, 255), duration=10.0):
        import time, math

        start = time.time()

        def scale(rgb, s):
            r, g, b = rgb
            return (int(r * s), int(g * s), int(b * s))

        # Phase A: strobe bursts (~6s)
        phase_a = 6.0
        strobe_dt = 0.08  # fast strobe
        while True:
            t = time.time() - start
            if t >= phase_a:
                break

            # every ~0.5s, do a quick burst sequence
            burst = int((t * 2) % 2)  # toggles every 0.5s
            base = team if burst == 0 else accent

            # 3 quick hits: base -> white -> base
            self.fill(base); time.sleep(strobe_dt)
            self.fill((255, 255, 255)); time.sleep(strobe_dt)
            self.fill(base); time.sleep(strobe_dt)
            self.fill((0, 0, 0)); time.sleep(strobe_dt)

        # Phase B: breathe pulse (~3s)
        phase_b = 3.0
        b_start = time.time()
        while True:
            t = time.time() - b_start
            if t >= phase_b:
                break
            # 0..1..0
            s = 0.25 + 0.75 * (0.5 - 0.5 * math.cos(2 * math.pi * (t / 0.8)))
            self.fill(scale(team, s))
            time.sleep(0.03)

        # Phase C: fade out (~1s)
        fade = 1.0
        f_start = time.time()
        while True:
            t = time.time() - f_start
            if t >= fade:
                break
            s = 1.0 - (t / fade)
            self.fill(scale(team, s))
            time.sleep(0.03)

        self.off()

    def goal_animation_chase(self, team=(255, 0, 0), tail=(255, 255, 255), duration=10.0, speed=0.02):
        import time

        n = self.strip.numPixels()
        start = time.time()

        def set_all_black():
            for i in range(n):
                self.strip.setPixelColor(i, Color(0, 0, 0))

        # moving head with a fading tail
        tail_len = max(6, n // 12)
        while (time.time() - start) < duration:
            t = time.time() - start
            head = int((t / speed)) % n

            set_all_black()

            # head = team
            self.strip.setPixelColor(head, _to_color(team))

            # tail behind head = white -> dim
            for k in range(1, tail_len + 1):
                idx = (head - k) % n
                s = max(0.0, 1.0 - (k / (tail_len + 1)))
                r, g, b = tail
                self.strip.setPixelColor(idx, Color(int(r * s), int(g * s), int(b * s)))

            self.strip.show()
            time.sleep(0.01)

        self.off()


    def goal_animation_sparkles(self, team=(255, 0, 0), duration=10.0):
        import time, random

        n = self.strip.numPixels()
        start = time.time()

        # ~8.5s sparkles
        while (time.time() - start) < (duration - 1.5):
            # decay background a bit by re-filling a dim base
            base = tuple(int(c * 0.15) for c in team)
            self.fill(base)

            # add random bright sparkles
            for _ in range(max(3, n // 15)):
                i = random.randrange(n)
                self.strip.setPixelColor(i, _to_color((255, 255, 255)))
            for _ in range(max(3, n // 15)):
                i = random.randrange(n)
                self.strip.setPixelColor(i, _to_color(team))

            self.strip.show()
            time.sleep(0.07)

        # 1.5s finale: 3 big flashes
        for _ in range(3):
            self.fill((255, 255, 255)); time.sleep(0.15)
            self.fill(team); time.sleep(0.20)
            self.fill((0, 0, 0)); time.sleep(0.15)

        self.off()


    def goal_flash(self, flashes=6, on=(255, 255, 255), off=(0, 0, 0), delay=0.12):
        import time
        for _ in range(flashes):
            self.fill(on)
            time.sleep(delay)
            self.fill(off)
            time.sleep(delay)

    def goal_animation_combo(self,team=(255, 0, 0),accent=(0, 120, 255),duration=10.0,):
        import time, math, random

        n = self.strip.numPixels()
        t0 = time.time()

        def scale(rgb, s):
            r, g, b = rgb
            return (int(r * s), int(g * s), int(b * s))

        def set_all(rgb):
            c = _to_color(rgb)
            for i in range(n):
                self.strip.setPixelColor(i, c)
            self.strip.show()

        def clear():
            for i in range(n):
                self.strip.setPixelColor(i, Color(0, 0, 0))

        # ----------------------------
        # Phase timings (sum ~ duration)
        # ----------------------------
        strobe_time = min(2.5, duration * 0.25)      # ~2.5s
        chase_time  = min(3.5, duration * 0.35)      # ~3.5s
        sparkle_time = max(0.0, duration - (strobe_time + chase_time + 1.5))  # leave 1.5s finale
        finale_time = duration - (strobe_time + chase_time + sparkle_time)

        # ----------------------------
        # Phase 1: Strobe bursts (team/accent/white)
        # ----------------------------
        strobe_dt = 0.08
        end1 = t0 + strobe_time
        while time.time() < end1:
            # quick burst: team -> white -> accent -> black
            set_all(team); time.sleep(strobe_dt)
            set_all((255, 255, 255)); time.sleep(strobe_dt)
            set_all(accent); time.sleep(strobe_dt)
            set_all((0, 0, 0)); time.sleep(strobe_dt)

        # ----------------------------
        # Phase 2: Chase with white tail + breathing background
        # ----------------------------
        end2 = end1 + chase_time
        tail_len = max(6, n // 12)
        step_dt = 0.015  # speed of movement
        while time.time() < end2:
            t = time.time() - end1
            head = int(t / step_dt) % n

            # breathing base (dim team color)
            breathe = 0.10 + 0.25 * (0.5 - 0.5 * math.cos(2 * math.pi * (t / 0.7)))
            base = scale(team, breathe)

            # draw base
            for i in range(n):
                self.strip.setPixelColor(i, _to_color(base))

            # head (accent)
            self.strip.setPixelColor(head, _to_color(accent))

            # tail (white fade)
            for k in range(1, tail_len + 1):
                idx = (head - k) % n
                s = max(0.0, 1.0 - (k / (tail_len + 1)))
                self.strip.setPixelColor(idx, _to_color(scale((255, 255, 255), s)))

            self.strip.show()
            time.sleep(0.01)

        # ----------------------------
        # Phase 3: Sparkles (team + white glitter)
        # ----------------------------
        end3 = end2 + sparkle_time
        while time.time() < end3:
            # dim base
            base = scale(team, 0.12)
            for i in range(n):
                self.strip.setPixelColor(i, _to_color(base))

            # random white sparkles
            for _ in range(max(3, n // 18)):
                i = random.randrange(n)
                self.strip.setPixelColor(i, _to_color((255, 255, 255)))

            # random accent sparkles
            for _ in range(max(2, n // 24)):
                i = random.randrange(n)
                self.strip.setPixelColor(i, _to_color(accent))

            self.strip.show()
            time.sleep(0.07)

        # ----------------------------
        # Phase 4: Finale (big flashes + fade out)
        # ----------------------------
        # Use whatever time remains (about 1.5s)
        # 2-3 punchy flashes, then fade
        punches = 3 if finale_time >= 1.4 else 2
        punch_on = 0.12
        punch_off = 0.10

        for _ in range(punches):
            set_all((255, 255, 255)); time.sleep(punch_on)
            set_all(team); time.sleep(punch_on)
            set_all((0, 0, 0)); time.sleep(punch_off)

        # fade out (rest)
        fade_left = max(0.2, (t0 + duration) - time.time())
        f0 = time.time()
        while True:
            t = time.time() - f0
            if t >= fade_left:
                break
            s = 1.0 - (t / fade_left)
            set_all(scale(team, s))
            time.sleep(0.03)

        self.off()