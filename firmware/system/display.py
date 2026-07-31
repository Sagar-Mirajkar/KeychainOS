"""KeychainOS ST7789 display driver for Waveshare ESP32-S3 LCD board."""

from machine import Pin, SPI
import framebuf
import os
import time

WIDTH = 240
HEIGHT = 320

LCD_SCLK = 1
LCD_MOSI = 2
LCD_MISO = 42
LCD_CS = 39
LCD_DC = 41
LCD_RST = 40
LCD_BL = 6
SD_CS = 38

SPI_ID = 2
SPI_FREQUENCY = 20_000_000

BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
CYAN = 0x07FF
MAGENTA = 0xF81F
YELLOW = 0xFFE0
ORANGE = 0xFD20
GREY = 0x8410
DARK_GREY = 0x4208
LIGHT_GREY = 0xC618


class ST7789:
    """Low-level ST7789 RGB565 display driver."""

    def __init__(self, width=WIDTH, height=HEIGHT, spi_frequency=SPI_FREQUENCY):
        self.width = width
        self.height = height
        self.spi_frequency = spi_frequency

        self.cs = Pin(LCD_CS, Pin.OUT, value=1)
        self.dc = Pin(LCD_DC, Pin.OUT, value=0)
        self.rst = Pin(LCD_RST, Pin.OUT, value=1)
        self.bl = Pin(LCD_BL, Pin.OUT, value=0)
        self.sd_cs = Pin(SD_CS, Pin.OUT, value=1)

        self.spi = SPI(
            SPI_ID,
            baudrate=self.spi_frequency,
            polarity=0,
            phase=0,
            sck=Pin(LCD_SCLK),
            mosi=Pin(LCD_MOSI),
            miso=Pin(LCD_MISO),
        )
        self.initialized = False

    def command(self, command_byte, data=None):
        """Send a command and optional data to the ST7789."""
        self.sd_cs.value(1)
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes((command_byte,)))
        if data is not None:
            self.dc.value(1)
            self.spi.write(data)
        self.cs.value(1)

    def hardware_reset(self):
        self.rst.value(1)
        time.sleep_ms(10)
        self.rst.value(0)
        time.sleep_ms(100)
        self.rst.value(1)
        time.sleep_ms(120)

    def init(self):
        """Initialize the display in 240 x 320 portrait RGB565 mode."""
        self.backlight_off()
        self.cs.value(1)
        self.sd_cs.value(1)
        self.hardware_reset()

        self.command(0x01)
        time.sleep_ms(150)
        self.command(0x11)
        time.sleep_ms(120)
        self.command(0x3A, b"\x55")
        self.command(0x36, b"\x00")
        self.command(0x21)
        self.command(0x13)
        self.command(0x29)
        time.sleep_ms(100)

        self.initialized = True
        self.fill(BLACK)
        self.backlight_on()

    def deinit(self):
        self.backlight_off()
        try:
            self.command(0x28)
            time.sleep_ms(20)
            self.command(0x10)
            time.sleep_ms(120)
        except Exception:
            pass
        try:
            self.spi.deinit()
        except Exception:
            pass
        self.initialized = False

    def set_spi_frequency(self, frequency):
        self.spi_frequency = int(frequency)
        self.spi.init(
            baudrate=self.spi_frequency,
            polarity=0,
            phase=0,
        )

    def backlight_on(self):
        self.bl.value(1)

    def backlight_off(self):
        self.bl.value(0)

    def set_backlight(self, enabled):
        self.bl.value(1 if enabled else 0)

    def set_window(self, x0, y0, x1, y1):
        self.command(
            0x2A,
            bytes((x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF)),
        )
        self.command(
            0x2B,
            bytes((y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF)),
        )
        self.command(0x2C)

    def _clip_rectangle(self, x, y, width, height):
        if width <= 0 or height <= 0:
            return None
        if x < 0:
            width += x
            x = 0
        if y < 0:
            height += y
            y = 0
        if x >= self.width or y >= self.height:
            return None
        if x + width > self.width:
            width = self.width - x
        if y + height > self.height:
            height = self.height - y
        if width <= 0 or height <= 0:
            return None
        return x, y, width, height

    def fill_rect(self, x, y, width, height, colour):
        clipped = self._clip_rectangle(x, y, width, height)
        if clipped is None:
            return
        x, y, width, height = clipped
        self.set_window(x, y, x + width - 1, y + height - 1)

        pixel = bytes(((colour >> 8) & 0xFF, colour & 0xFF))
        chunk_pixels = 512
        chunk = pixel * chunk_pixels
        count = width * height

        self.sd_cs.value(1)
        self.cs.value(0)
        self.dc.value(1)
        for _ in range(count // chunk_pixels):
            self.spi.write(chunk)
        remaining = count % chunk_pixels
        if remaining:
            self.spi.write(pixel * remaining)
        self.cs.value(1)

    def fill(self, colour):
        self.fill_rect(0, 0, self.width, self.height, colour)

    def fill_screen(self, colour):
        self.fill(colour)

    def horizontal_line(self, x, y, width, colour):
        self.fill_rect(x, y, width, 1, colour)

    def vertical_line(self, x, y, height, colour):
        self.fill_rect(x, y, 1, height, colour)

    def outline_rect(self, x, y, width, height, colour, thickness=1):
        if width <= 0 or height <= 0:
            return
        thickness = max(1, int(thickness))
        self.fill_rect(x, y, width, thickness, colour)
        self.fill_rect(x, y + height - thickness, width, thickness, colour)
        self.fill_rect(x, y, thickness, height, colour)
        self.fill_rect(x + width - thickness, y, thickness, height, colour)

    def write_rgb565(self, x, y, width, height, data):
        if x < 0 or y < 0 or x + width > self.width or y + height > self.height:
            raise ValueError("RGB565 region is outside the display")
        expected = width * height * 2
        if len(data) != expected:
            raise ValueError("RGB565 data length mismatch")

        self.set_window(x, y, x + width - 1, y + height - 1)
        self.sd_cs.value(1)
        self.cs.value(0)
        self.dc.value(1)
        for start in range(0, len(data), 4096):
            self.spi.write(data[start:start + 4096])
        self.cs.value(1)

    def write_rgb565_file(
        self,
        filename,
        x=0,
        y=0,
        width=WIDTH,
        height=HEIGHT,
        chunk_size=4096,
    ):
        expected = width * height * 2
        file_size = os.stat(filename)[6]
        if file_size != expected:
            raise ValueError("RGB565 file size mismatch")

        self.set_window(x, y, x + width - 1, y + height - 1)
        self.sd_cs.value(1)
        self.cs.value(0)
        self.dc.value(1)
        with open(filename, "rb") as image_file:
            while True:
                chunk = image_file.read(chunk_size)
                if not chunk:
                    break
                self.spi.write(chunk)
        self.cs.value(1)

    @staticmethod
    def _swap_byte_pairs(data):
        for index in range(0, len(data), 2):
            data[index], data[index + 1] = data[index + 1], data[index]

    def draw_text(
        self,
        text,
        x,
        y,
        colour=WHITE,
        background=BLACK,
        width=None,
        height=16,
    ):
        text = str(text)
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return
        if width is None:
            width = self.width - x
        width = min(int(width), self.width - x)
        height = min(int(height), self.height - y)
        if width <= 0 or height <= 0:
            return

        buffer = bytearray(width * height * 2)
        framebuffer = framebuf.FrameBuffer(buffer, width, height, framebuf.RGB565)
        framebuffer.fill(background)
        framebuffer.text(text, 0, 4, colour)
        self._swap_byte_pairs(buffer)
        self.write_rgb565(x, y, width, height, buffer)

    def centred_text(self, text, y, colour=WHITE, background=BLACK):
        text = str(text)[: self.width // 8]
        text_width = max(8, len(text) * 8)
        x = (self.width - text_width) // 2
        self.draw_text(text, x, y, colour, background, text_width)

    def dimensions(self):
        return self.width, self.height

    @staticmethod
    def colour565(red, green, blue):
        red = max(0, min(255, int(red)))
        green = max(0, min(255, int(green)))
        blue = max(0, min(255, int(blue)))
        return ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)


_default_display = None


def get_display():
    """Return the shared KeychainOS display instance."""
    global _default_display
    if _default_display is None:
        _default_display = ST7789()
    return _default_display
