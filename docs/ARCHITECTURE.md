# Architecture

## ESP32-S3

Always-on primary controller for the interface, local storage, touch, controls, simple games, IR, NFC, sensors, audio, status and power management.

## Radxa Zero 3W

Future on-demand Linux subsystem for ESP flashing, terminal and SSH, Python, USB-heavy work, larger downloads, file processing and heavier emulation.

## Communication

UART is the initial control plane for commands and status. A higher-speed data plane may later use USB, Wi-Fi or another validated interface.

## Radxa power states

- Off
- Background Linux
- Interactive Linux

Linux must perform a clean shutdown before ESP32 disables the Radxa power rail.
