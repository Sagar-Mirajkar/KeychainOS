"""KeychainOS OTA Python-module download test.

Downloads ota/update_test.py from GitHub, saves it locally as
/update_test.py, then imports and runs the downloaded module.
This test does not modify main.py or boot.py.
"""

import gc
import network
import time

from wifi_secrets import WIFI_NAME, WIFI_PASSWORD

try:
    import requests
except ImportError:
    import urequests as requests

MODULE_URL = (
    "https://raw.githubusercontent.com/"
    "Sagar-Mirajkar/KeychainOS/"
    "refs/heads/main/ota/update_test.py"
)

TEMP_FILE = "/update_test.py.new"
FINAL_FILE = "/update_test.py"


def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    if wifi.isconnected():
        print("Wi-Fi already connected")
        print(wifi.ifconfig())
        return wifi

    print("Connecting to:", WIFI_NAME)
    wifi.connect(WIFI_NAME, WIFI_PASSWORD)

    started = time.ticks_ms()

    while not wifi.isconnected():
        print(".", end="")
        time.sleep_ms(500)

        if time.ticks_diff(time.ticks_ms(), started) > 30000:
            raise RuntimeError("Wi-Fi connection timed out")

    print()
    print("WIFI CONNECTED")
    print(wifi.ifconfig())
    return wifi


def download_module():
    print("Downloading module:")
    print(MODULE_URL)

    gc.collect()
    response = None

    try:
        response = requests.get(MODULE_URL)
        status = getattr(response, "status_code", 200)
        print("HTTP status:", status)

        if status != 200:
            raise RuntimeError("HTTP error {}".format(status))

        data = response.content

        if not data:
            raise RuntimeError("Downloaded module is empty")

        print("Downloaded bytes:", len(data))

        with open(TEMP_FILE, "wb") as output:
            output.write(data)

    finally:
        if response is not None:
            response.close()


def validate_module():
    source = open(TEMP_FILE, "r").read()
    compile(source, TEMP_FILE, "exec")
    print("Downloaded Python syntax: OK")


def install_module():
    import os

    try:
        os.remove(FINAL_FILE)
    except OSError:
        pass

    os.rename(TEMP_FILE, FINAL_FILE)
    print("Installed as:", FINAL_FILE)


def run_downloaded_module():
    import sys

    if "update_test" in sys.modules:
        del sys.modules["update_test"]

    import update_test

    print("Imported downloaded module")
    result = update_test.run()
    print("Module returned:", result)

    if result is not True:
        raise RuntimeError("Downloaded module returned an unexpected result")

    print("OTA PYTHON MODULE TEST PASSED")


def run():
    print()
    print("===================================")
    print("KeychainOS OTA Python Module Test")
    print("===================================")

    connect_wifi()
    download_module()
    validate_module()
    install_module()
    run_downloaded_module()


run()
