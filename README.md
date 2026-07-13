# KeychainOS

KeychainOS is a portable ESP32-S3 pocket utility computer built around the Waveshare ESP32-S3 LCD Driver Board and the Waveshare 2-inch capacitive-touch LCD.

## Project purpose

KeychainOS is intended to remain instantly available through the ESP32-S3 and provide on-demand Linux capability through a future Radxa Zero 3W subsystem when a phone cannot complete the required task.

## Planned capabilities

- Touch-based KeychainOS interface
- Physical controls and small games
- microSD storage and file browsing
- IR learning and universal remote control
- NFC automation
- Audio, motion sensing and vibration
- USB programming, storage and host modes
- On-demand Linux tools, ESP flashing and heavier retro gaming

## Current core hardware

- Waveshare ESP32-S3 LCD Driver Board
- ESP32-S3-WROOM-1-N8R8
- 8 MB flash and 8 MB PSRAM
- Waveshare 2-inch capacitive-touch LCD
- ST7789T3 display controller
- CST816D touch controller
- Display-side microSD card

## Current graphics baseline

TFT_eSPI is the known-good display library. Other graphics libraries have shown blank output, incorrect scaling, incorrect position or missing backlight behaviour and are not the current baseline.

## Repository structure

- `assets/` — Icons, fonts, images and themes
- `config/` — TFT_eSPI setup and version records
- `docs/` — Project documentation
- `firmware/` — Main firmware and independent diagnostics
- `hardware/` — Pinouts, schematics, datasheets and enclosure work
- `notes/` — Working notes and decisions
- `research/` — SBC, Linux, USB and component research
- `sd-card/` — Reference structure for the ESP-side microSD card
