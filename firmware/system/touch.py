"""KeychainOS CST816D capacitive touch driver.

Hardware:
- Waveshare ESP32-S3 LCD Driver Board
- CST816D touch controller
- 240 x 320 portrait display
"""

from machine import I2C, Pin
import time

SCREEN_WIDTH = 240
SCREEN_HEIGHT = 320

TP_SDA = 15
TP_SCL = 7
TP_RST = 16
TP_INT = 17
TP_ADDRESS = 0x15

I2C_ID = 1
I2C_FREQUENCY = 400_000

DEFAULT_SWIPE_THRESHOLD = 35
GAME_SWIPE_THRESHOLD = 24
RELEASE_SAMPLES = 3
SAMPLE_DELAY_MS = 10
LONG_PRESS_MS = 700
LONG_PRESS_MOVE_TOLERANCE = 12


class CST816D:
    """CST816D touch controller with tap, swipe, and long-press support."""

    def __init__(
        self,
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        swap_xy=False,
        invert_x=False,
        invert_y=False,
    ):
        self.width = width
        self.height = height
        self.swap_xy = bool(swap_xy)
        self.invert_x = bool(invert_x)
        self.invert_y = bool(invert_y)

        self.reset_pin = Pin(TP_RST, Pin.OUT, value=1)
        self.interrupt_pin = Pin(TP_INT, Pin.IN, Pin.PULL_UP)
        self.i2c = I2C(
            I2C_ID,
            scl=Pin(TP_SCL),
            sda=Pin(TP_SDA),
            freq=I2C_FREQUENCY,
        )

        self.available = False
        self.chip_id = None

    def hardware_reset(self):
        """Reset the CST816D controller."""
        self.reset_pin.value(0)
        time.sleep_ms(200)
        self.reset_pin.value(1)
        time.sleep_ms(300)

    def scan(self):
        """Return all I2C addresses visible on the touch bus."""
        return self.i2c.scan()

    def init(self):
        """Reset and detect the CST816D controller."""
        self.hardware_reset()
        devices = self.scan()
        self.available = TP_ADDRESS in devices
        if not self.available:
            return False

        try:
            self.chip_id = self.i2c.readfrom_mem(TP_ADDRESS, 0xA7, 1)[0]
        except OSError:
            self.chip_id = None

        return True

    def set_transform(self, swap_xy=None, invert_x=None, invert_y=None):
        """Update coordinate transformation options."""
        if swap_xy is not None:
            self.swap_xy = bool(swap_xy)
        if invert_x is not None:
            self.invert_x = bool(invert_x)
        if invert_y is not None:
            self.invert_y = bool(invert_y)

    def transform(self, raw_x, raw_y):
        """Transform raw coordinates into display coordinates."""
        x = int(raw_x)
        y = int(raw_y)

        if self.swap_xy:
            x, y = y, x
        if self.invert_x:
            x = self.width - 1 - x
        if self.invert_y:
            y = self.height - 1 - y

        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        return x, y

    def read(self):
        """Return current touch coordinates as (x, y), or None."""
        if not self.available:
            return None

        try:
            touch_count = self.i2c.readfrom_mem(TP_ADDRESS, 0x02, 1)[0]
            if touch_count == 0:
                return None

            data = self.i2c.readfrom_mem(TP_ADDRESS, 0x03, 4)
            raw_x = ((data[0] & 0x0F) << 8) | data[1]
            raw_y = ((data[2] & 0x0F) << 8) | data[3]
            return self.transform(raw_x, raw_y)

        except OSError:
            return None

    def touched(self):
        """Return True while at least one touch is present."""
        return self.read() is not None

    def wait_for_touch(self):
        """Block until a touch begins and return its first coordinates."""
        while True:
            point = self.read()
            if point is not None:
                return point
            time.sleep_ms(SAMPLE_DELAY_MS)

    def wait_for_release(self, release_samples=RELEASE_SAMPLES):
        """Block until the finger has left the screen."""
        missing = 0
        while True:
            if self.read() is None:
                missing += 1
                if missing >= release_samples:
                    return
            else:
                missing = 0
            time.sleep_ms(SAMPLE_DELAY_MS)

    def capture_contact(self, release_samples=RELEASE_SAMPLES):
        """Capture one complete contact and return its movement details."""
        start = self.wait_for_touch()
        end = start
        started_at = time.ticks_ms()
        missing = 0

        while True:
            point = self.read()
            if point is not None:
                end = point
                missing = 0
            else:
                missing += 1
                if missing >= release_samples:
                    break
            time.sleep_ms(SAMPLE_DELAY_MS)

        duration = time.ticks_diff(time.ticks_ms(), started_at)
        return {
            "start": start,
            "end": end,
            "dx": end[0] - start[0],
            "dy": end[1] - start[1],
            "duration_ms": duration,
        }

    def capture_gesture(
        self,
        swipe_threshold=DEFAULT_SWIPE_THRESHOLD,
        long_press_ms=LONG_PRESS_MS,
        move_tolerance=LONG_PRESS_MOVE_TOLERANCE,
    ):
        """Wait for and classify one tap, swipe, or long press.

        Returns a dictionary containing:
        type, x, y, start_x, start_y, dx, dy, duration_ms.
        """
        contact = self.capture_contact()
        start_x, start_y = contact["start"]
        end_x, end_y = contact["end"]
        dx = contact["dx"]
        dy = contact["dy"]
        duration = contact["duration_ms"]

        if (
            duration >= long_press_ms
            and abs(dx) <= move_tolerance
            and abs(dy) <= move_tolerance
        ):
            gesture_type = "LONG_PRESS"
        elif abs(dx) >= swipe_threshold and abs(dx) > abs(dy):
            gesture_type = "LEFT" if dx < 0 else "RIGHT"
        elif abs(dy) >= swipe_threshold and abs(dy) > abs(dx):
            gesture_type = "UP" if dy < 0 else "DOWN"
        else:
            gesture_type = "TAP"

        return {
            "type": gesture_type,
            "x": end_x,
            "y": end_y,
            "start_x": start_x,
            "start_y": start_y,
            "dx": dx,
            "dy": dy,
            "duration_ms": duration,
        }

    def poll_gesture(self, swipe_threshold=GAME_SWIPE_THRESHOLD):
        """Return a gesture only when currently touched, otherwise None.

        This method is suitable for game loops.
        """
        first = self.read()
        if first is None:
            return None

        start = first
        end = first
        started_at = time.ticks_ms()
        missing = 0

        while True:
            point = self.read()
            if point is not None:
                end = point
                missing = 0
            else:
                missing += 1
                if missing >= 2:
                    break
            time.sleep_ms(5)

        dx = end[0] - start[0]
        dy = end[1] - start[1]
        duration = time.ticks_diff(time.ticks_ms(), started_at)

        if abs(dx) >= swipe_threshold and abs(dx) > abs(dy):
            gesture_type = "LEFT" if dx < 0 else "RIGHT"
        elif abs(dy) >= swipe_threshold and abs(dy) > abs(dx):
            gesture_type = "UP" if dy < 0 else "DOWN"
        elif (
            duration >= LONG_PRESS_MS
            and abs(dx) <= LONG_PRESS_MOVE_TOLERANCE
            and abs(dy) <= LONG_PRESS_MOVE_TOLERANCE
        ):
            gesture_type = "LONG_PRESS"
        else:
            gesture_type = "TAP"

        return {
            "type": gesture_type,
            "x": end[0],
            "y": end[1],
            "start_x": start[0],
            "start_y": start[1],
            "dx": dx,
            "dy": dy,
            "duration_ms": duration,
        }

    def wait_gesture(self, timeout_ms=None, swipe_threshold=DEFAULT_SWIPE_THRESHOLD):
        """Wait for one complete gesture, or return None after timeout."""
        started = time.ticks_ms()
        while True:
            if self.read() is not None:
                return self.capture_gesture(
                    swipe_threshold=swipe_threshold
                )
            if (
                timeout_ms is not None
                and time.ticks_diff(time.ticks_ms(), started) >= timeout_ms
            ):
                return None
            time.sleep_ms(SAMPLE_DELAY_MS)

    @staticmethod
    def hit_test(point, x, y, width, height):
        """Return True when a point is inside a rectangular touch target."""
        if point is None:
            return False
        point_x, point_y = point
        return x <= point_x < x + width and y <= point_y < y + height

    @staticmethod
    def gesture_tuple(gesture):
        """Convert a gesture dictionary to the legacy tuple format."""
        if gesture is None:
            return None
        return gesture["type"], gesture["x"], gesture["y"]


_default_touch = None


def get_touch():
    """Return the shared KeychainOS touch instance."""
    global _default_touch
    if _default_touch is None:
        _default_touch = CST816D()
    return _default_touch
