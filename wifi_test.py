"""Minimal Wi-Fi test for MicroPython ESP32-S3."""

import network
import time

from wifi_secrets import WIFI_NAME, WIFI_PASSWORD

wifi = network.WLAN(network.STA_IF)
wifi.active(True)

print("Connecting to:", WIFI_NAME)

if not wifi.isconnected():
    wifi.connect(WIFI_NAME, WIFI_PASSWORD)

    start = time.ticks_ms()

    while not wifi.isconnected():
        print(".", end="")
        time.sleep_ms(500)

        if time.ticks_diff(time.ticks_ms(), start) > 30000:
            break

print()

if wifi.isconnected():
    print("WIFI CONNECTED")
    print(wifi.ifconfig())
else:
    print("WIFI CONNECTION FAILED")
    print("Status:", wifi.status())
