"""KeychainOS safe OTA updater test with backup and rollback.

Test target: /update_test.py
Remote source: ota/update_test.py in the public GitHub repository.

Safety sequence:
1. Connect to Wi-Fi.
2. Download to /update_test.py.new.
3. Validate downloaded Python syntax.
4. Move current /update_test.py to /update_test.py.bak.
5. Install the new file.
6. Import and run the new module.
7. Delete the backup only after the test succeeds.
8. Restore the backup automatically if installation or testing fails.

This script does not modify /main.py or /boot.py.
"""

import gc
import network
import os
import sys
import time

from wifi_secrets import WIFI_NAME, WIFI_PASSWORD

try:
    import requests
except ImportError:
    import urequests as requests

SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "Sagar-Mirajkar/KeychainOS/"
    "refs/heads/main/ota/update_test.py"
)

TARGET_FILE = "/update_test.py"
TEMP_FILE = "/update_test.py.new"
BACKUP_FILE = "/update_test.py.bak"
MODULE_NAME = "update_test"


def exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def remove_if_present(path):
    try:
        os.remove(path)
    except OSError:
        pass


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


def download_to_temp():
    print("Downloading update:")
    print(SOURCE_URL)

    remove_if_present(TEMP_FILE)
    gc.collect()
    response = None

    try:
        response = requests.get(SOURCE_URL)
        status = getattr(response, "status_code", 200)
        print("HTTP status:", status)

        if status != 200:
            raise RuntimeError("HTTP error {}".format(status))

        data = response.content

        if not data:
            raise RuntimeError("Downloaded update is empty")

        print("Downloaded bytes:", len(data))

        with open(TEMP_FILE, "wb") as output:
            output.write(data)

    finally:
        if response is not None:
            response.close()


def validate_temp():
    with open(TEMP_FILE, "r") as source_file:
        source = source_file.read()

    compile(source, TEMP_FILE, "exec")
    print("Downloaded Python syntax: OK")


def create_backup():
    remove_if_present(BACKUP_FILE)

    if exists(TARGET_FILE):
        os.rename(TARGET_FILE, BACKUP_FILE)
        print("Backup created:", BACKUP_FILE)
    else:
        print("No existing target; no backup required")


def install_temp():
    os.rename(TEMP_FILE, TARGET_FILE)
    print("Installed update as:", TARGET_FILE)


def unload_module():
    if MODULE_NAME in sys.modules:
        del sys.modules[MODULE_NAME]


def test_installed_module():
    unload_module()
    module = __import__(MODULE_NAME)
    print("Imported installed module")

    result = module.run()
    print("Module returned:", result)

    if result is not True:
        raise RuntimeError("Updated module returned an unexpected result")

    print("Installed module test: PASS")


def rollback():
    print("ROLLBACK STARTED")
    unload_module()
    remove_if_present(TEMP_FILE)
    remove_if_present(TARGET_FILE)

    if exists(BACKUP_FILE):
        os.rename(BACKUP_FILE, TARGET_FILE)
        print("Backup restored:", TARGET_FILE)
    else:
        print("No backup was available to restore")


def finish_success():
    remove_if_present(BACKUP_FILE)
    remove_if_present(TEMP_FILE)
    print("Backup removed after successful validation")
    print("SAFE OTA UPDATE TEST PASSED")


def run():
    print()
    print("===================================")
    print("KeychainOS Safe OTA Update Test")
    print("===================================")

    connect_wifi()
    download_to_temp()
    validate_temp()

    try:
        create_backup()
        install_temp()
        test_installed_module()
    except Exception as error:
        print("UPDATE VALIDATION FAILED:")
        print(repr(error))
        rollback()
        raise

    finish_success()


run()
