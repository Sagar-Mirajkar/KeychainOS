# Hardware

## Core

- Waveshare ESP32-S3 LCD Driver Board
- ESP32-S3-WROOM-1-N8R8
- 8 MB flash
- 8 MB PSRAM
- Waveshare 2-inch capacitive-touch LCD
- ST7789T3 display controller
- CST816D touch controller
- microSD card slot
- Integrated ETA6096 battery management

## Official LCD Driver Board pin mapping

### LCD and shared SPI

- GPIO1 — SCLK
- GPIO2 — MOSI
- GPIO42 — MISO
- GPIO39 — LCD CS
- GPIO41 — LCD DC
- GPIO40 — LCD reset
- GPIO6 — LCD backlight

### Touch

- GPIO15 — SDA
- GPIO7 — SCL
- GPIO16 — reset
- GPIO17 — interrupt

### SD

- GPIO38 — SD CS
- GPIO1/GPIO2/GPIO42 — shared SPI bus

## Planned peripherals

- Physical joystick and buttons
- MAX98357 I2S amplifier and speaker
- IR receiver and transmitter array
- NFC reader
- Accelerometer and compass
- Vibration motor
- Radxa Zero 3W
- Single-port USB role switching
- Controlled Radxa power rail
