"""Shared ST7789 display driver for KeychainOS."""

from machine import Pin, SPI
import framebuf
import time

from system.colours import BLACK, WHITE, DARK_BG

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
SPI_FREQUENCY = 20_000_000

lcd_cs = Pin(LCD_CS, Pin.OUT, value=1)
lcd_dc = Pin(LCD_DC, Pin.OUT, value=0)
lcd_rst = Pin(LCD_RST, Pin.OUT, value=1)
lcd_bl = Pin(LCD_BL, Pin.OUT, value=0)
sd_cs = Pin(SD_CS, Pin.OUT, value=1)

spi = SPI(
    2,
    baudrate=SPI_FREQUENCY,
    polarity=0,
    phase=0,
    sck=Pin(LCD_SCLK),
    mosi=Pin(LCD_MOSI),
    miso=Pin(LCD_MISO)
)


def command(command_byte, data=None):
    """Send a command and optional data to the ST7789."""
    sd_cs.value(1)
    lcd_cs.value(0)
    lcd_dc.value(0)
    spi.write(bytes([command_byte]))

    if data is not None:
        lcd_dc.value(1)
        spi.write(data)

    lcd_cs.value(1)


def hardware_reset():
    lcd_rst.value(1)
    time.sleep_ms(10)
    lcd_rst.value(0)
    time.sleep_ms(100)
    lcd_rst.value(1)
    time.sleep_ms(120)


def init():
    print("Initializing ST7789 display")
    lcd_bl.value(0)
    lcd_cs.value(1)
    sd_cs.value(1)

    hardware_reset()

    command(0x01)
    time.sleep_ms(150)
    command(0x11)
    time.sleep_ms(120)
    command(0x3A, b"\x55")
    command(0x36, b"\x00")
    command(0x21)
    command(0x13)
    command(0x29)
    time.sleep_ms(100)

    fill_screen(BLACK)
    lcd_bl.value(1)
    print("ST7789 display ready")


def set_backlight(enabled):
    lcd_bl.value(1 if enabled else 0)


def set_window(x0, y0, x1, y1):
    command(0x2A, bytes([
        x0 >> 8, x0 & 0xFF,
        x1 >> 8, x1 & 0xFF
    ]))

    command(0x2B, bytes([
        y0 >> 8, y0 & 0xFF,
        y1 >> 8, y1 & 0xFF
    ]))

    command(0x2C)


def fill_rect(x, y, width, height, colour):
    if width <= 0 or height <= 0:
        return

    if x < 0:
        width += x
        x = 0

    if y < 0:
        height += y
        y = 0

    if x >= WIDTH or y >= HEIGHT:
        return

    if x + width > WIDTH:
        width = WIDTH - x

    if y + height > HEIGHT:
        height = HEIGHT - y

    if width <= 0 or height <= 0:
        return

    set_window(x, y, x + width - 1, y + height - 1)

    pixel = bytes([
        (colour >> 8) & 0xFF,
        colour & 0xFF
    ])

    chunk_pixels = 256
    chunk = pixel * chunk_pixels
    total_pixels = width * height

    sd_cs.value(1)
    lcd_cs.value(0)
    lcd_dc.value(1)

    for _ in range(total_pixels // chunk_pixels):
        spi.write(chunk)

    remaining = total_pixels % chunk_pixels
    if remaining:
        spi.write(pixel * remaining)

    lcd_cs.value(1)


def fill_screen(colour):
    fill_rect(0, 0, WIDTH, HEIGHT, colour)


def horizontal_line(x, y, width, colour):
    fill_rect(x, y, width, 1, colour)


def vertical_line(x, y, height, colour):
    fill_rect(x, y, 1, height, colour)


def outline_rect(x, y, width, height, colour, thickness=1):
    if thickness < 1:
        thickness = 1

    fill_rect(x, y, width, thickness, colour)
    fill_rect(x, y + height - thickness, width, thickness, colour)
    fill_rect(x, y, thickness, height, colour)
    fill_rect(x + width - thickness, y, thickness, height, colour)


def _swap_byte_pairs(data):
    for index in range(0, len(data), 2):
        data[index], data[index + 1] = data[index + 1], data[index]


def draw_text(text, x, y, colour=WHITE, background=DARK_BG,
              width=None, height=16):
    text = str(text)

    if width is None:
        width = WIDTH - x

    if x < 0:
        x = 0

    if y < 0:
        y = 0

    if x >= WIDTH or y >= HEIGHT:
        return

    width = min(width, WIDTH - x)
    height = min(height, HEIGHT - y)

    if width <= 0 or height <= 0:
        return

    text_buffer = bytearray(width * height * 2)
    text_framebuffer = framebuf.FrameBuffer(
        text_buffer,
        width,
        height,
        framebuf.RGB565
    )

    text_framebuffer.fill(background)
    text_framebuffer.text(text, 0, 4, colour)
    _swap_byte_pairs(text_buffer)

    set_window(x, y, x + width - 1, y + height - 1)

    sd_cs.value(1)
    lcd_cs.value(0)
    lcd_dc.value(1)

    for start in range(0, len(text_buffer), 2048):
        spi.write(text_buffer[start:start + 2048])

    lcd_cs.value(1)


def centred_text(text, y, colour=WHITE, background=DARK_BG):
    text = str(text)
    maximum_characters = WIDTH // 8

    if len(text) > maximum_characters:
        text = text[:maximum_characters]

    text_width = len(text) * 8
    x = (WIDTH - text_width) // 2
    draw_text(text, x, y, colour, background, text_width)


def trim_text(text, character_limit):
    text = str(text)

    if len(text) <= character_limit:
        return text

    if character_limit <= 3:
        return text[:character_limit]

    return text[:character_limit - 3] + "..."
