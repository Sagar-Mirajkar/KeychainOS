"""KeychainOS ST7789 display driver.

Hardware:
- Waveshare ESP32-S3 LCD Driver Board
- ST7789T3 display
- 240 x 320 portrait orientation
- Shared LCD and microSD SPI bus
"""

from machine import Pin, SPI
import framebuf
import time


# =========================================================
# DISPLAY CONFIGURATION
# =========================================================

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


# =========================================================
# COMMON RGB565 COLOURS
# =========================================================

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


# =========================================================
# ST7789 DRIVER
# =========================================================

class ST7789:
    """Low-level ST7789 RGB565 display driver."""

    def __init__(
        self,
        width=WIDTH,
        height=HEIGHT,
        spi_frequency=SPI_FREQUENCY
    ):
        self.width = width
        self.height = height
        self.spi_frequency = spi_frequency

        self.cs = Pin(
            LCD_CS,
            Pin.OUT,
            value=1
        )

        self.dc = Pin(
            LCD_DC,
            Pin.OUT,
            value=0
        )

        self.rst = Pin(
            LCD_RST,
            Pin.OUT,
            value=1
        )

        self.bl = Pin(
            LCD_BL,
            Pin.OUT,
            value=0
        )

        # The LCD and microSD card share the SPI bus.
        # Keep the SD card deselected during LCD operations.
        self.sd_cs = Pin(
            SD_CS,
            Pin.OUT,
            value=1
        )

        self.spi = SPI(
            SPI_ID,
            baudrate=self.spi_frequency,
            polarity=0,
            phase=0,
            sck=Pin(LCD_SCLK),
            mosi=Pin(LCD_MOSI),
            miso=Pin(LCD_MISO)
        )

        self.initialized = False

    # =====================================================
    # LOW-LEVEL COMMUNICATION
    # =====================================================

    def command(self, command_byte, data=None):
        """Send one command and optional data to the ST7789."""

        self.sd_cs.value(1)

        self.cs.value(0)
        self.dc.value(0)

        self.spi.write(
            bytes((command_byte,))
        )

        if data is not None:
            self.dc.value(1)
            self.spi.write(data)

        self.cs.value(1)

    def hardware_reset(self):
        """Perform an ST7789 hardware reset."""

        self.rst.value(1)
        time.sleep_ms(10)

        self.rst.value(0)
        time.sleep_ms(100)

        self.rst.value(1)
        time.sleep_ms(120)

    def init(self):
        """Initialize the ST7789 display controller."""

        self.backlight_off()

        self.cs.value(1)
        self.sd_cs.value(1)

        self.hardware_reset()

        # Software reset.
        self.command(0x01)
        time.sleep_ms(150)

        # Exit sleep mode.
        self.command(0x11)
        time.sleep_ms(120)

        # RGB565, 16 bits per pixel.
        self.command(
            0x3A,
            b"\x55"
        )

        # Portrait orientation.
        self.command(
            0x36,
            b"\x00"
        )

        # Enable display inversion.
        self.command(0x21)

        # Normal display mode.
        self.command(0x13)

        # Display on.
        self.command(0x29)
        time.sleep_ms(100)

        self.initialized = True

        self.fill(BLACK)
        self.backlight_on()

    def deinit(self):
        """Turn off the display and release the SPI interface."""

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
        """Change the display SPI frequency."""

        self.spi_frequency = int(frequency)

        self.spi.init(
            baudrate=self.spi_frequency,
            polarity=0,
            phase=0
        )

    # =====================================================
    # BACKLIGHT
    # =====================================================

    def backlight_on(self):
        """Turn the LCD backlight on."""

        self.bl.value(1)

    def backlight_off(self):
        """Turn the LCD backlight off."""

        self.bl.value(0)

    def set_backlight(self, enabled):
        """Set the backlight state."""

        self.bl.value(
            1 if enabled else 0
        )

    # =====================================================
    # DRAWING WINDOW
    # =====================================================

    def set_window(
        self,
        x0,
        y0,
        x1,
        y1
    ):
        """Set the rectangular ST7789 drawing region."""

        self.command(
            0x2A,
            bytes((
                (x0 >> 8) & 0xFF,
                x0 & 0xFF,
                (x1 >> 8) & 0xFF,
                x1 & 0xFF
            ))
        )

        self.command(
            0x2B,
            bytes((
                (y0 >> 8) & 0xFF,
                y0 & 0xFF,
                (y1 >> 8) & 0xFF,
                y1 & 0xFF
            ))
        )

        self.command(0x2C)

    def _clip_rectangle(
        self,
        x,
        y,
        width,
        height
    ):
        """Clip a rectangle to the display boundaries."""

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

        return (
            x,
            y,
            width,
            height
        )

    # =====================================================
    # RECTANGLES AND LINES
    # =====================================================

    def fill_rect(
        self,
        x,
        y,
        width,
        height,
        colour
    ):
        """Draw a solid RGB565 rectangle."""

        clipped = self._clip_rectangle(
            x,
            y,
            width,
            height
        )

        if clipped is None:
            return

        x, y, width, height = clipped

        self.set_window(
            x,
            y,
            x + width - 1,
            y + height - 1
        )

        pixel = bytes((
            (colour >> 8) & 0xFF,
            colour & 0xFF
        ))

        chunk_pixels = 512
        chunk = pixel * chunk_pixels

        total_pixels = width * height
        full_chunks = (
            total_pixels
            // chunk_pixels
        )

        remaining_pixels = (
            total_pixels
            % chunk_pixels
        )

        self.sd_cs.value(1)

        self.cs.value(0)
        self.dc.value(1)

        for _ in range(full_chunks):
            self.spi.write(chunk)

        if remaining_pixels:
            self.spi.write(
                pixel * remaining_pixels
            )

        self.cs.value(1)

    def fill(self, colour):
        """Fill the entire screen with one colour."""

        self.fill_rect(
            0,
            0,
            self.width,
            self.height,
            colour
        )

    def fill_screen(self, colour):
        """Compatibility alias for fill()."""

        self.fill(colour)

    def horizontal_line(
        self,
        x,
        y,
        width,
        colour
    ):
        """Draw a horizontal line."""

        self.fill_rect(
            x,
            y,
            width,
            1,
            colour
        )

    def vertical_line(
        self,
        x,
        y,
        height,
        colour
    ):
        """Draw a vertical line."""

        self.fill_rect(
            x,
            y,
            1,
            height,
            colour
        )

    def outline_rect(
        self,
        x,
        y,
        width,
        height,
        colour,
        thickness=1
    ):
        """Draw a rectangular outline."""

        if width <= 0 or height <= 0:
            return

        thickness = max(
            1,
            int(thickness)
        )

        maximum_thickness = min(
            width // 2,
            height // 2
        )

        if maximum_thickness > 0:
            thickness = min(
                thickness,
                maximum_thickness
            )

        self.fill_rect(
            x,
            y,
            width,
            thickness,
            colour
        )

        self.fill_rect(
            x,
            y + height - thickness,
            width,
            thickness,
            colour
        )

        self.fill_rect(
            x,
            y,
            thickness,
            height,
            colour
        )

        self.fill_rect(
            x + width - thickness,
            y,
            thickness,
            height,
            colour
        )

    # =====================================================
    # RAW PIXEL DATA
    # =====================================================

    def write_rgb565(
        self,
        x,
        y,
        width,
        height,
        data
    ):
        """Write big-endian RGB565 pixel data to a display region.

        The data length must be width * height * 2 bytes.
        """

        clipped = self._clip_rectangle(
            x,
            y,
            width,
            height
        )

        if clipped is None:
            return

        clipped_x, clipped_y, clipped_w, clipped_h = clipped

        if (
            clipped_x != x
            or clipped_y != y
            or clipped_w != width
            or clipped_h != height
        ):
            raise ValueError(
                "write_rgb565 region must fit inside screen"
            )

        expected_length = (
            width
            * height
            * 2
        )

        if len(data) != expected_length:
            raise ValueError(
                "RGB565 data length mismatch"
            )

        self.set_window(
            x,
            y,
            x + width - 1,
            y + height - 1
        )

        self.sd_cs.value(1)

        self.cs.value(0)
        self.dc.value(1)

        for start in range(
            0,
            len(data),
            4096
        ):
            self.spi.write(
                data[
                    start:start + 4096
                ]
            )

        self.cs.value(1)

    def write_rgb565_file(
        self,
        filename,
        x=0,
        y=0,
        width=WIDTH,
        height=HEIGHT,
        chunk_size=4096
    ):
        """Stream a big-endian RGB565 file to the display."""

        expected_size = (
            width
            * height
            * 2
        )

        try:
            file_size = os.stat(
                filename
            )[6]

        except NameError:
            import os

            file_size = os.stat(
                filename
            )[6]

        if file_size != expected_size:
            raise ValueError(
                "RGB565 file size mismatch"
            )

        self.set_window(
            x,
            y,
            x + width - 1,
            y + height - 1
        )

        self.sd_cs.value(1)

        self.cs.value(0)
        self.dc.value(1)

        with open(
            filename,
            "rb"
        ) as image_file:
            while True:
                chunk = image_file.read(
                    chunk_size
                )

                if not chunk:
                    break

                self.spi.write(chunk)

        self.cs.value(1)

    # =====================================================
    # BUILT-IN TEXT
    # =====================================================

    @staticmethod
    def _swap_byte_pairs(data):
        """Convert framebuf RGB565 byte order for the ST7789."""

        for index in range(
            0,
            len(data),
            2
        ):
            first = data[index]

            data[index] = (
                data[index + 1]
            )

            data[index + 1] = first

    def draw_text(
        self,
        text,
        x,
        y,
        colour=WHITE,
        background=BLACK,
        width=None,
        height=16
    ):
        """Draw text using MicroPython's built-in 8 x 8 font."""

        text = str(text)

        if x < 0 or y < 0:
            return

        if x >= self.width or y >= self.height:
            return

        if width is None:
            width = (
                self.width
                - x
            )

        width = min(
            int(width),
            self.width - x
        )

        height = min(
            int(height),
            self.height - y
        )

        if width <= 0 or height <= 0:
            return

        text_buffer = bytearray(
            width
            * height
            * 2
        )

        framebuffer = framebuf.FrameBuffer(
            text_buffer,
            width,
            height,
            framebuf.RGB565
        )

        framebuffer.fill(
            background
        )

        framebuffer.text(
            text,
            0,
            4,
            colour
        )

        self._swap_byte_pairs(
            text_buffer
        )

        self.write_rgb565(
            x,
            y,
            width,
            height,
            text_buffer
        )

    def centred_text(
        self,
        text,
        y,
        colour=WHITE,
        background=BLACK
    ):
        """Draw horizontally centred text."""

        text = str(text)

        maximum_characters = (
            self.width
            // 8
        )

        if len(text) > maximum_characters:
            text = text[
                :maximum_characters
            ]

        text_width = max(
            8,
            len(text) * 8
        )

        x = (
            self.width
            - text_width
        ) // 2

        self.draw_text(
            text,
            x,
            y,
            colour,
            background,
            text_width
        )

    # =====================================================
    # UTILITY FUNCTIONS
    # =====================================================

    def dimensions(self):
        """Return display width and height."""

        return (
            self.width,
            self.height
        )

    def colour565(
        self,
        red,
        green,
        blue
    ):
        """Convert 8-bit RGB values to RGB565."""

        red = max(
            0,
            min(255, int(red))
        )

        green = max(
            0,
            min(255, int(green))
        )

        blue = max(
            0,
            min(255, int(blue))
        )

        return (
            ((red & 0xF8) << 8)
            | ((green & 0xFC) << 3)
            | (blue >> 3)
        )


# =========================================================
# OPTIONAL SHARED INSTANCE
# =========================================================

_default_display = None


def get_display():
    """Return the shared KeychainOS display instance."""

    global _default_display

    if _default_display is None:
        _default_display = ST7789()

    return _default_display
