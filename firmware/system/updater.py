"""KeychainOS flat-folder transactional updater.

Reads /update/update.json from GitHub. Each entry maps a unique flat
source filename to its intended destination path on the ESP.
"""

import gc
import json
import os

try:
    import uhashlib as hashlib
except ImportError:
    import hashlib

try:
    import ubinascii as binascii
except ImportError:
    import binascii


UPDATE_BASE_URL = (
    "https://raw.githubusercontent.com/"
    "Sagar-Mirajkar/KeychainOS/refs/heads/main/update/"
)

UPDATE_MANIFEST_URL = UPDATE_BASE_URL + "update.json"
CHUNK_SIZE = 1024
DOWNLOAD_RETRIES = 4


def exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def make_directories(path):
    current = ""

    for part in path.split("/"):
        if not part:
            continue

        current += "/" + part

        if not exists(current):
            os.mkdir(current)


def parent_directory(path):
    position = path.rfind("/")

    if position <= 0:
        return "/"

    return path[:position]


def remove_if_present(path):
    try:
        os.remove(path)
    except OSError:
        pass


def sha256_file(path):
    digest = hashlib.sha256()

    with open(path, "rb") as source:
        while True:
            block = source.read(CHUNK_SIZE)

            if not block:
                break

            digest.update(block)

    return binascii.hexlify(digest.digest()).decode()


def requests_module():
    try:
        import requests
        return requests
    except ImportError:
        import urequests
        return urequests


def response_status(response):
    return getattr(
        response,
        "status_code",
        getattr(response, "status", 200)
    )


def response_bytes(response):
    if hasattr(response, "content"):
        return response.content

    if hasattr(response, "raw"):
        blocks = []

        while True:
            block = response.raw.read(CHUNK_SIZE)

            if not block:
                break

            blocks.append(block)

        return b"".join(blocks)

    return response.text.encode("utf-8")


def download_manifest():
    response = requests_module().get(UPDATE_MANIFEST_URL)

    try:
        status = response_status(response)

        if status != 200:
            raise RuntimeError(
                "Update manifest HTTP {}".format(status)
            )

        manifest = json.loads(
            response_bytes(response).decode("utf-8")
        )

    finally:
        response.close()

    if manifest.get("format") != 1:
        raise ValueError("Unsupported update manifest format")

    if not isinstance(manifest.get("files"), list):
        raise ValueError("Update manifest files must be a list")

    return manifest


def validate_entry(entry):
    source = entry.get("source")
    destination = entry.get("destination")
    expected = entry.get("sha256")

    if not source or "/" in source or "\\" in source:
        raise ValueError("Invalid flat update source")

    if not destination or not destination.startswith("/"):
        raise ValueError("Invalid update destination")

    if not expected or len(expected) != 64:
        raise ValueError("Invalid update SHA-256")

    return source, destination, expected.lower()


def download_file(source, destination):
    url = UPDATE_BASE_URL + source
    last_error = None

    for attempt in range(1, DOWNLOAD_RETRIES + 1):
        response = None

        try:
            response = requests_module().get(url)
            status = response_status(response)

            if status != 200:
                raise RuntimeError(
                    "HTTP {} for {}".format(status, source)
                )

            with open(destination, "wb") as output:
                if hasattr(response, "raw"):
                    while True:
                        block = response.raw.read(CHUNK_SIZE)

                        if not block:
                            break

                        output.write(block)

                elif hasattr(response, "content"):
                    output.write(response.content)

                else:
                    output.write(
                        response.text.encode("utf-8")
                    )

            return

        except Exception as error:
            last_error = error
            remove_if_present(destination)

            if attempt < DOWNLOAD_RETRIES:
                import time
                time.sleep_ms(attempt * 1000)

        finally:
            if response is not None:
                response.close()

    raise last_error


def installed_version():
    path = "/data/system/version.json"

    try:
        with open(path, "r") as source:
            return json.load(source).get("version", "unknown")
    except Exception:
        return "unknown"


def save_installed_version(version):
    path = "/data/system/version.json"
    make_directories(parent_directory(path))
    temporary = path + ".new"

    with open(temporary, "w") as output:
        json.dump(
            {
                "version": version
            },
            output
        )

    remove_if_present(path)
    os.rename(temporary, path)


def check(progress=None):
    """Return update metadata without installing anything."""

    manifest = download_manifest()
    changed = []

    for index, entry in enumerate(manifest["files"]):
        source, destination, expected = validate_entry(entry)

        if progress is not None:
            progress(
                index + 1,
                len(manifest["files"]),
                destination,
                "check"
            )

        if not exists(destination):
            changed.append(entry)
            continue

        if sha256_file(destination) != expected:
            changed.append(entry)

        gc.collect()

    return {
        "installed_version": installed_version(),
        "available_version": manifest.get("version", "unknown"),
        "restart_required": bool(
            manifest.get("restart_required", True)
        ),
        "changed": changed,
        "manifest": manifest
    }


def install(progress=None):
    """Install only missing or changed files transactionally."""

    status = check(progress)
    manifest = status["manifest"]
    changed = status["changed"]

    if not changed:
        return {
            "updated": 0,
            "up_to_date": True,
            "restart_required": False,
            "version": manifest.get("version", "unknown")
        }

    pending = []

    for index, entry in enumerate(changed):
        source, destination, expected = validate_entry(entry)
        make_directories(parent_directory(destination))
        temporary = destination + ".new"

        if (
            exists(temporary)
            and sha256_file(temporary) == expected
        ):
            state = "resume"
        else:
            remove_if_present(temporary)
            state = "download"

            if progress is not None:
                progress(
                    index + 1,
                    len(changed),
                    destination,
                    state
                )

            download_file(source, temporary)

        actual = sha256_file(temporary)

        if actual != expected:
            remove_if_present(temporary)
            raise ValueError(
                "SHA-256 mismatch: {}".format(destination)
            )

        if destination.endswith(".py"):
            with open(temporary, "r") as source_file:
                compile(
                    source_file.read(),
                    destination,
                    "exec"
                )

        pending.append((destination, temporary))
        gc.collect()

    backups = []
    installed = []

    try:
        for destination, temporary in pending:
            backup = destination + ".bak"
            remove_if_present(backup)

            if exists(destination):
                os.rename(destination, backup)
                backups.append((destination, backup))

            os.rename(temporary, destination)
            installed.append(destination)

        save_installed_version(
            manifest.get("version", "unknown")
        )

        for destination, backup in backups:
            remove_if_present(backup)

    except Exception:
        for destination in installed:
            remove_if_present(destination)

        for destination, backup in reversed(backups):
            if exists(backup):
                os.rename(backup, destination)

        raise

    return {
        "updated": len(installed),
        "up_to_date": False,
        "restart_required": bool(
            manifest.get("restart_required", True)
        ),
        "version": manifest.get("version", "unknown")
    }
