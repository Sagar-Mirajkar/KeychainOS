"""KeychainOS main.py OTA boot recovery guard."""

import os


MAIN_FILE = "/main.py"
BACKUP_FILE = "/main.py.bak"

PENDING_MARKER = "/ota_main_pending"
TESTING_MARKER = "/ota_main_testing"


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


def restore_backup():
    """Restore the previous working main.py."""

    print("OTA recovery: restoring main.py backup")

    remove_if_present(MAIN_FILE)

    if not exists(BACKUP_FILE):
        print("OTA recovery error: main.py.bak not found")
        return False

    os.rename(
        BACKUP_FILE,
        MAIN_FILE
    )

    remove_if_present(
        PENDING_MARKER
    )

    remove_if_present(
        TESTING_MARKER
    )

    print("OTA recovery: main.py restored")

    return True


def on_boot():
    """Run from boot.py before MicroPython starts main.py."""

    # The previous test boot did not get confirmed.
    # Restore the last working main.py.
    if exists(TESTING_MARKER):
        print("OTA recovery: failed test boot detected")

        return restore_backup()

    # A new main.py was installed.
    # Allow one test boot.
    if exists(PENDING_MARKER):
        print("OTA recovery: starting test boot")

        os.rename(
            PENDING_MARKER,
            TESTING_MARKER
        )

        return True

    return True


def confirm():
    """Call from the new main.py after successful startup."""

    if exists(TESTING_MARKER):
        remove_if_present(
            TESTING_MARKER
        )

        remove_if_present(
            BACKUP_FILE
        )

        print("OTA recovery: new main.py confirmed")

    return True