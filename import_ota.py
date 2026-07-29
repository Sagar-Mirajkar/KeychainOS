"""Safe KeychainOS OTA download test."""

import gc
import network
import time

from wifi_secrets import WIFI_NAME, WIFI_PASSWORD

try:
    import requests
except ImportError:
    import urequests as requests


TEST_FILE_URL = (
    "https://raw.githubusercontent.com/"
    "Sagar-Mirajkar/KeychainOS/"
    "refs/heads/main/ota/hello.txt"
)

OUTPUT_FILE = "/ota_download.txt"


def connect_wifi():
    wifi = network.WLAN(
        network.STA_IF
    )

    wifi.active(True)

    if wifi.isconnected():
        print("Wi-Fi already connected")
        print(wifi.ifconfig())
        return wifi

    print("Connecting to:", WIFI_NAME)

    wifi.connect(
        WIFI_NAME,
        WIFI_PASSWORD
    )

    start_time = time.ticks_ms()

    while not wifi.isconnected():
        print(".", end="")
        time.sleep_ms(500)

        elapsed = time.ticks_diff(
            time.ticks_ms(),
            start_time
        )

        if elapsed > 30000:
            raise RuntimeError(
                "Wi-Fi connection timed out"
            )

    print()
    print("WIFI CONNECTED")
    print(wifi.ifconfig())

    return wifi


def download_file():
    print("Downloading:")
    print(TEST_FILE_URL)

    gc.collect()

    response = None

    try:
        response = requests.get(
            TEST_FILE_URL
        )

        status_code = getattr(
            response,
            "status_code",
            200
        )

        print(
            "HTTP status:",
            status_code
        )

        if status_code != 200:
            raise RuntimeError(
                "HTTP error: {}".format(
                    status_code
                )
            )

        data = response.content

        if not data:
            raise RuntimeError(
                "Downloaded file is empty"
            )

        print(
            "Downloaded bytes:",
            len(data)
        )

        with open(
            OUTPUT_FILE,
            "wb"
        ) as output:
            output.write(data)

    finally:
        if response is not None:
            response.close()


def verify_file():
    with open(
        OUTPUT_FILE,
        "rb"
    ) as downloaded_file:
        data = downloaded_file.read()

    print("Saved as:", OUTPUT_FILE)

    print()
    print("Downloaded content:")
    print("-------------------")

    try:
        print(
            data.decode("utf-8")
        )

    except Exception:
        print(data)

    print("-------------------")
    print("OTA DOWNLOAD TEST PASSED")


def run():
    print()
    print("==============================")
    print("KeychainOS OTA Download Test")
    print("==============================")

    connect_wifi()
    download_file()
    verify_file()


run()