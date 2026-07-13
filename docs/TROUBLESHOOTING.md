# Troubleshooting

## Known observations

- Successful Arduino upload proves the ESP32-S3 bootloader, USB link and flash process are functional.
- The ST7789 display can retain the previous frame while powered.
- An old image remaining after a new upload does not mean the old firmware is still running.
- A new sketch must initialise the LCD and clear display RAM.
- Power-cycle the entire board when a newly flashed sketch does not correctly initialise the panel.

## Independent validation order

1. Serial output
2. Backlight
3. Display
4. Touch
5. SD card
6. Combined operation

Do not debug several unknown subsystems in one sketch.
