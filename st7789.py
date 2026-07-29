"""Minimal ST7789 driver for the Waveshare ESP32-S3 LCD Driver Board."""

from machine import Pin, SPI
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

BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
CYAN = 0x07FF
YELLOW = 0xFFE0
MAGENTA = 0xF81F
ORANGE = 0xFD20


class ST7789:
    def __init__(self, baudrate=20_000_000):
        self.width = WIDTH
        self.height = HEIGHT

        self.cs = Pin(LCD_CS, Pin.OUT, value=1)
        self.dc = Pin(LCD_DC, Pin.OUT, value=0)
        self.rst = Pin(LCD_RST, Pin.OUT, value=1)
        self.backlight = Pin(LCD_BL, Pin.OUT, value=0)
        self.sd_cs = Pin(SD_CS, Pin.OUT, value=1)

        self.spi = SPI(
            2,
            baudrate=baudrate,
            polarity=0,
            phase=0,
            sck=Pin(LCD_SCLK),
            mosi=Pin(LCD_MOSI),
            miso=Pin(LCD_MISO)
        )

    def command(self, command_byte, data=None):
        self.sd_cs.value(1)
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes([command_byte]))

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
        self.backlight.value(0)
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

        self.fill(BLACK)
        self.backlight.value(1)

    def set_window(self, x0, y0, x1, y1):
        self.command(
            0x2A,
            bytes([
                x0 >> 8,
                x0 & 0xFF,
                x1 >> 8,
                x1 & 0xFF
            ])
        )

        self.command(
            0x2B,
            bytes([
                y0 >> 8,
                y0 & 0xFF,
                y1 >> 8,
                y1 & 0xFF
            ])
        )

        self.command(0x2C)

    def fill_rect(self, x, y, width, height, colour):
        if width <= 0 or height <= 0:
            return

        if x < 0:
            width += x
            x = 0

        if y < 0:
            height += y
            y = 0

        if x >= self.width or y >= self.height:
            return

        if x + width > self.width:
            width = self.width - x

        if y + height > self.height:
            height = self.height - y

        if width <= 0 or height <= 0:
            return

        self.set_window(x, y, x + width - 1, y + height - 1)

        pixel = bytes([
            (colour >> 8) & 0xFF,
            colour & 0xFF
        ])

        chunk_pixels = 512
        chunk = pixel * chunk_pixels
        total_pixels = width * height

        self.sd_cs.value(1)
        self.cs.value(0)
        self.dc.value(1)

        for _ in range(total_pixels // chunk_pixels):
            self.spi.write(chunk)

        remaining = total_pixels % chunk_pixels
        if remaining:
            self.spi.write(pixel * remaining)

        self.cs.value(1)

    def fill(self, colour):
        self.fill_rect(0, 0, self.width, self.height, colour)

    def outline_rect(self, x, y, width, height, colour, thickness=1):
        self.fill_rect(x, y, width, thickness, colour)
        self.fill_rect(x, y + height - thickness, width, thickness, colour)
        self.fill_rect(x, y, thickness, height, colour)
        self.fill_rect(x + width - thickness, y, thickness, height, colour)

    def backlight_on(self):
        self.backlight.value(1)

    def backlight_off(self):
        self.backlight.value(0)
