"""CST816D touch driver for the Waveshare 2-inch touch display."""

from machine import Pin, I2C
import time

SCREEN_WIDTH = 240
SCREEN_HEIGHT = 320

TP_SDA = 15
TP_SCL = 7
TP_RST = 16
TP_INT = 17
TP_ADDRESS = 0x15

TOUCH_SWAP_XY = False
TOUCH_INVERT_X = False
TOUCH_INVERT_Y = False

SWIPE_THRESHOLD = 35
RELEASE_SAMPLES = 3
SAMPLE_DELAY_MS = 10


class CST816D:
    def __init__(self):
        self.reset_pin = Pin(TP_RST, Pin.OUT, value=1)
        self.interrupt_pin = Pin(TP_INT, Pin.IN, Pin.PULL_UP)

        self.i2c = I2C(
            1,
            scl=Pin(TP_SCL),
            sda=Pin(TP_SDA),
            freq=400_000
        )

    def hardware_reset(self):
        self.reset_pin.value(0)
        time.sleep_ms(200)
        self.reset_pin.value(1)
        time.sleep_ms(300)

    def init(self):
        print("Initializing CST816D touch")

        self.hardware_reset()
        devices = self.i2c.scan()

        print(
            "Touch I2C devices:",
            [hex(address) for address in devices]
        )

        if TP_ADDRESS not in devices:
            print("Touch controller not found")
            return False

        try:
            chip_id = self.i2c.readfrom_mem(
                TP_ADDRESS,
                0xA7,
                1
            )[0]

            print("Touch chip ID:", hex(chip_id))

        except OSError as error:
            print("Could not read touch chip ID:", error)

        print("CST816D touch ready")
        return True

    def transform(self, raw_x, raw_y):
        x = raw_x
        y = raw_y

        if TOUCH_SWAP_XY:
            x, y = y, x

        if TOUCH_INVERT_X:
            x = SCREEN_WIDTH - 1 - x

        if TOUCH_INVERT_Y:
            y = SCREEN_HEIGHT - 1 - y

        return x, y

    def read(self):
        try:
            touch_count = self.i2c.readfrom_mem(
                TP_ADDRESS,
                0x02,
                1
            )[0]

            if touch_count == 0:
                return None

            data = self.i2c.readfrom_mem(
                TP_ADDRESS,
                0x03,
                4
            )

            raw_x = ((data[0] & 0x0F) << 8) | data[1]
            raw_y = ((data[2] & 0x0F) << 8) | data[3]

            return self.transform(raw_x, raw_y)

        except OSError:
            return None

    def capture_gesture(self, swipe_threshold=SWIPE_THRESHOLD):
        start_point = None
        end_point = None
        missing_samples = 0

        while True:
            point = self.read()

            if point is not None:
                missing_samples = 0

                if start_point is None:
                    start_point = point

                end_point = point

            elif start_point is not None:
                missing_samples += 1

                if missing_samples >= RELEASE_SAMPLES:
                    break

            time.sleep_ms(SAMPLE_DELAY_MS)

        if start_point is None or end_point is None:
            return None

        delta_x = end_point[0] - start_point[0]
        delta_y = end_point[1] - start_point[1]

        print(
            "Gesture:",
            start_point,
            "to",
            end_point,
            "delta",
            delta_x,
            delta_y
        )

        if (
            abs(delta_x) >= swipe_threshold
            and abs(delta_x) > abs(delta_y)
        ):
            direction = "LEFT" if delta_x < 0 else "RIGHT"
            return direction, end_point[0], end_point[1]

        if (
            abs(delta_y) >= swipe_threshold
            and abs(delta_y) > abs(delta_x)
        ):
            direction = "UP" if delta_y < 0 else "DOWN"
            return direction, end_point[0], end_point[1]

        return "TAP", end_point[0], end_point[1]

    def poll_gesture(self, swipe_threshold=24):
        first_point = self.read()

        if first_point is None:
            return None

        start_point = first_point
        end_point = first_point
        missing_samples = 0

        while True:
            point = self.read()

            if point is not None:
                end_point = point
                missing_samples = 0

            else:
                missing_samples += 1

                if missing_samples >= 2:
                    break

            time.sleep_ms(5)

        delta_x = end_point[0] - start_point[0]
        delta_y = end_point[1] - start_point[1]

        if (
            abs(delta_x) >= swipe_threshold
            and abs(delta_x) > abs(delta_y)
        ):
            return "LEFT" if delta_x < 0 else "RIGHT"

        if (
            abs(delta_y) >= swipe_threshold
            and abs(delta_y) > abs(delta_x)
        ):
            return "UP" if delta_y < 0 else "DOWN"

        return "TAP"

    def wait_for_release(self):
        missing_samples = 0

        while True:
            point = self.read()

            if point is None:
                missing_samples += 1

                if missing_samples >= RELEASE_SAMPLES:
                    return

            else:
                missing_samples = 0

            time.sleep_ms(SAMPLE_DELAY_MS)
