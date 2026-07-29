from pathlib import Path
from PIL import Image, ImageOps

# Input image
INPUT_FILE = Path(
    r"C:\Users\HO1704\Downloads\PASSPORT PHOTO.jpg"
)

# Output files
OUTPUT_RGB565 = Path(
    r"C:\Users\HO1704\Downloads\passport_photo.rgb"
)

OUTPUT_PREVIEW = Path(
    r"C:\Users\HO1704\Downloads\passport_photo_preview.png"
)

# Waveshare display resolution
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320


def rgb888_to_rgb565_big_endian(red, green, blue):
    """
    Convert one RGB888 pixel to RGB565.

    Returns the high byte followed by the low byte,
    matching the byte order used by the working
    MicroPython ST7789 SPI code.
    """

    rgb565 = (
        ((red & 0xF8) << 8)
        | ((green & 0xFC) << 3)
        | (blue >> 3)
    )

    high_byte = (rgb565 >> 8) & 0xFF
    low_byte = rgb565 & 0xFF

    return high_byte, low_byte


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input image not found:\n{INPUT_FILE}"
        )

    print(f"Opening: {INPUT_FILE}")

    with Image.open(INPUT_FILE) as source_image:
        # Apply orientation information stored by phones/cameras
        source_image = ImageOps.exif_transpose(source_image)

        # Ensure standard RGB format
        source_image = source_image.convert("RGB")

        print(f"Original size: {source_image.size}")

        # Resize proportionally and crop from the centre to 240 x 320
        display_image = ImageOps.fit(
            source_image,
            (DISPLAY_WIDTH, DISPLAY_HEIGHT),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5)
        )

        # Save a normal preview so the result can be checked
        display_image.save(OUTPUT_PREVIEW)

        # Convert to raw RGB565
        rgb565_data = bytearray(
            DISPLAY_WIDTH * DISPLAY_HEIGHT * 2
        )

        output_index = 0

        for red, green, blue in display_image.getdata():
            high_byte, low_byte = rgb888_to_rgb565_big_endian(
                red,
                green,
                blue
            )

            rgb565_data[output_index] = high_byte
            rgb565_data[output_index + 1] = low_byte
            output_index += 2

        OUTPUT_RGB565.write_bytes(rgb565_data)

    expected_size = DISPLAY_WIDTH * DISPLAY_HEIGHT * 2
    actual_size = OUTPUT_RGB565.stat().st_size

    print()
    print("Conversion completed.")
    print(f"Preview: {OUTPUT_PREVIEW}")
    print(f"RGB565 file: {OUTPUT_RGB565}")
    print(f"Expected size: {expected_size:,} bytes")
    print(f"Actual size:   {actual_size:,} bytes")

    if actual_size == expected_size:
        print("PASS: RGB565 file size is correct.")
    else:
        print("FAIL: RGB565 file size is incorrect.")


if __name__ == "__main__":
    main()