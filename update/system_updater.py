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
    """Return True when a file or directory exists."""

    try:
        os.stat(path)
        return True

    except OSError:
        return False


def make_directories(path):
    """Create a directory and any missing parents."""

    current = ""

    for part in path.split("/"):
        if not part:
            continue

        current += "/" + part

        if not exists(current):
            os.mkdir(current)


def parent_directory(path):
    """Return the parent directory of a path."""

    position = path.rfind("/")

    if position <= 0:
        return "/"

    return path[:position]


def remove_if_present(path):
    """Remove a file if it exists."""

    try:
        os.remove(path)

    except OSError:
        pass


def sha256_file(path):
    """Return the lowercase SHA-256 hex digest of a file."""

    digest = hashlib.sha256()

    with open(path, "rb") as source:
        while True:
            block = source.read(
                CHUNK_SIZE
            )

            if not block:
                break

            digest.update(block)

    return binascii.hexlify(
        digest.digest()
    ).decode()


def requests_module():
    """Return the available MicroPython HTTP module."""

    try:
        import requests
        return requests

    except ImportError:
        import urequests
        return urequests


def response_status(response):
    """Return the HTTP status from a response."""

    return getattr(
        response,
        "status_code",
        getattr(
            response,
            "status",
            200
        )
    )


def response_bytes(response):
    """Read all bytes from a small HTTP response."""

    if hasattr(response, "content"):
        return response.content

    if hasattr(response, "raw"):
        blocks = []

        while True:
            block = response.raw.read(
                CHUNK_SIZE
            )

            if not block:
                break

            blocks.append(block)

        return b"".join(blocks)

    return response.text.encode(
        "utf-8"
    )


def download_manifest():
    """Download and validate update/update.json."""

    response = requests_module().get(
        UPDATE_MANIFEST_URL
    )

    try:
        status = response_status(
            response
        )

        if status != 200:
            raise RuntimeError(
                "Update manifest HTTP {}"
                .format(status)
            )

        manifest = json.loads(
            response_bytes(
                response
            ).decode("utf-8")
        )

    finally:
        response.close()

    if manifest.get("format") != 1:
        raise ValueError(
            "Unsupported update manifest format"
        )

    if not isinstance(
        manifest.get("files"),
        list
    ):
        raise ValueError(
            "Update manifest files must be a list"
        )

    return manifest


def validate_entry(entry):
    """Validate one flat update mapping entry."""

    source = entry.get("source")
    destination = entry.get(
        "destination"
    )
    expected = entry.get("sha256")

    if (
        not source
        or "/" in source
        or "\\" in source
    ):
        raise ValueError(
            "Invalid flat update source"
        )

    if (
        not destination
        or not destination.startswith("/")
    ):
        raise ValueError(
            "Invalid update destination"
        )

    if (
        not expected
        or len(expected) != 64
    ):
        raise ValueError(
            "Invalid update SHA-256"
        )

    return (
        source,
        destination,
        expected.lower()
    )


def download_file(
    source,
    destination
):
    """Download one flat update file with retries."""

    url = (
        UPDATE_BASE_URL
        + source
    )

    last_error = None

    for attempt in range(
        1,
        DOWNLOAD_RETRIES + 1
    ):
        response = None

        try:
            response = (
                requests_module().get(
                    url
                )
            )

            status = response_status(
                response
            )

            if status != 200:
                raise RuntimeError(
                    "HTTP {} for {}"
                    .format(
                        status,
                        source
                    )
                )

            with open(
                destination,
                "wb"
            ) as output:
                if hasattr(
                    response,
                    "raw"
                ):
                    while True:
                        block = (
                            response.raw.read(
                                CHUNK_SIZE
                            )
                        )

                        if not block:
                            break

                        output.write(block)

                elif hasattr(
                    response,
                    "content"
            
