"""KeychainOS filesystem bootstrap."""

import os


REQUIRED_DIRECTORIES = (
    "/apps",
    "/apps/games",
    "/apps/tools",
    "/apps/organizer",
    "/apps/remote",
    "/apps/connections",
    "/apps/developer",
    "/apps/settings",
    "/apps/about",
    "/themes",
    "/data",
    "/data/system",
    "/data/apps",
    "/media",
    "/media/images",
    "/media/animations",
    "/media/text",
    "/media/documents",
    "/media/incoming",
    "/media/originals",
    "/media/unsupported",
    "/media/failed",
    "/packages",
    "/packages/incoming",
    "/packages/installed",
    "/packages/backups",
    "/packages/failed",
    "/cache",
    "/cache/icons",
    "/cache/thumbnails",
    "/cache/temporary",
    "/logs",
    "/logs/system",
    "/logs/apps",
    "/logs/updates",
    "/trash",
    "/trash/apps",
    "/trash/files",
    "/trash/themes",
    "/disabled",
    "/disabled/games",
    "/disabled/tools",
    "/disabled/organizer",
    "/disabled/remote",
    "/disabled/connections",
    "/disabled/developer",
    "/disabled/settings",
    "/disabled/themes",
    "/recovery",
    "/recovery/backups",
    "/recovery/pending",
    "/recovery/failed",
    "/lost+found",
)


def exists(path):
    """Return True when a file or directory exists."""

    try:
        os.stat(path)
        return True

    except OSError:
        return False


def make_directory(path):
    """Create a directory and any missing parent directories."""

    current = ""

    for part in path.split("/"):
        if not part:
            continue

        current += "/" + part

        if not exists(current):
            os.mkdir(current)


def ensure_structure():
    """Create all missing KeychainOS directories."""

    created = 0

    for directory in REQUIRED_DIRECTORIES:
        if not exists(directory):
            make_directory(directory)
            created += 1

    return created
