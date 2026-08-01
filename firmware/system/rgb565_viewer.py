"""Stream big-endian RGB565 images to the 240 x 320 display."""
import os

WIDTH = 240
HEIGHT = 320
FULL_SCREEN_BYTES = WIDTH * HEIGHT * 2


def file_info(path):
    size = os.stat(path)[6]
    return {"path": path, "size": size, "full_screen": size == FULL_SCREEN_BYTES}


def show(display, path, width=WIDTH, height=HEIGHT, x=0, y=0):
    expected = width * height * 2
    actual = os.stat(path)[6]
    if actual != expected:
        raise ValueError("RGB565 size must be %d bytes" % expected)
    display.write_rgb565_file(path, x=x, y=y, width=width, height=height)
    return True
