# Software Setup

## Baseline

- Arduino IDE
- ESP32 board package by Espressif Systems
- Board target: ESP32S3 Dev Module
- Graphics baseline: TFT_eSPI

## Rule

Record exact versions and board settings before upgrading any library or board package.

## Current observation

TFT_eSPI examples operate correctly. Other display libraries have shown blank output, missing backlight behaviour, wrong dimensions or wrong offsets. KeychainOS v0.1 should therefore use TFT_eSPI.
