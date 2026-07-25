"""Deliberately failing OTA rollback test."""

VERSION = "0.3-ROLLBACK-TEST"


def run():
    print("Running deliberately failing update")
    print("OTA module version:", VERSION)

    # False deliberately triggers automatic rollback.
    return False
