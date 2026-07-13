# Current Status

## Confirmed

- ESP32-S3 accepts firmware through Arduino IDE.
- TFT_eSPI examples render correctly on the Waveshare display.
- Ribbon cable, LCD SPI path, backlight and panel operate with TFT_eSPI.
- Official LCD Driver Board GPIO mappings are documented.

## Current baseline

- Board: Waveshare ESP32-S3 LCD Driver Board
- Display: Waveshare 2-inch capacitive-touch LCD
- Graphics: TFT_eSPI
- Resolution: 240 x 320
- Orientation: Portrait initially

## Current issue history

Sketches using some other display libraries produced blank screens, incorrect scaling, incorrect positioning or failed to control the backlight. The ST7789 panel can retain the previous frame when a newly flashed sketch does not initialise and clear the display correctly.

## Next milestone

1. Save the known-good TFT_eSPI configuration.
2. Run independent backlight, display, touch and SD diagnostics.
3. Build the first KeychainOS home-screen mock-up.
4. Add touch navigation.
5. Add SD-backed settings and file browsing.
