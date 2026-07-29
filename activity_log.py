"""Persistent activity and event logging for KeychainOS.

Records boot events, app launches, exits, failures, file installs/removals,
and custom system events. Logs are stored as line-oriented JSON in:

    /keychainos_logs/events.jsonl

A filesystem snapshot is compared at boot to detect added, removed, and
changed root-level files. Sensitive file contents are never recorded.
"""

import gc
import json
import os
import time

LOG_DIR = "/keychainos_logs"
LOG_FILE = LOG_DIR + "/events.jsonl"
SNAPSHOT_FILE = LOG_DIR + "/filesystem_snapshot.json"
MAX_LOG_BYTES = 65536
BACKUP_LOG = LOG_DIR + "/events.previous.jsonl"


def _ensure_directory():
    try:
        os.mkdir(LOG_DIR)
    except OSError:
        pass


def _timestamp():
    values = time.localtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
        values[0], values[1], values[2],
        values[3], values[4], values[5]
    )


def _rotate_if_needed():
    try:
        size = os.stat(LOG_FILE)[6]
    except OSError:
        return

    if size < MAX_LOG_BYTES:
        return

    try:
        os.remove(BACKUP_LOG)
    except OSError:
        pass

    try:
        os.rename(LOG_FILE, BACKUP_LOG)
    except OSError:
        pass


def record(event, category="SYSTEM", status="INFO", details=None):
    """Append one structured event without raising into the caller."""

    try:
        _ensure_directory()
        _rotate_if_needed()

        item = {
            "time": _timestamp(),
            "uptime_ms": time.ticks_ms(),
            "category": str(category),
            "event": str(event),
            "status": str(status),
            "free_memory": gc.mem_free(),
        }

        if details is not None:
            item["details"] = details

        with open(LOG_FILE, "a") as output:
            output.write(json.dumps(item))
            output.write("\n")

        return True

    except Exception:
        return False


def exception(source, error):
    return record(
        "EXCEPTION",
        "ERROR",
        "FAILED",
        {
            "source": str(source),
            "type": error.__class__.__name__,
            "message": str(error),
            "repr": repr(error),
        }
    )


def app_launch(name, module_name):
    return record(
        "APP_LAUNCH",
        "APPLICATION",
        "STARTED",
        {"name": name, "module": module_name}
    )


def app_exit(name, result=None):
    return record(
        "APP_EXIT",
        "APPLICATION",
        "COMPLETED",
        {"name": name, "result": str(result)}
    )


def setting_changed(name, old_value, new_value):
    return record(
        "SETTING_CHANGED",
        "SETTINGS",
        "COMPLETED",
        {
            "name": name,
            "old": str(old_value),
            "new": str(new_value),
        }
    )


def update_event(action, status, details=None):
    return record(action, "UPDATE", status, details)


def _root_snapshot():
    snapshot = {}

    try:
        names = os.listdir("/")
    except OSError:
        return snapshot

    for name in names:
        path = "/" + name

        if path == LOG_DIR:
            continue

        try:
            stat = os.stat(path)
            snapshot[name] = {
                "mode": stat[0],
                "size": stat[6],
            }
        except OSError:
            pass

    return snapshot


def _load_snapshot():
    try:
        with open(SNAPSHOT_FILE, "r") as source:
            value = json.load(source)
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _save_snapshot(snapshot):
    temporary = SNAPSHOT_FILE + ".new"

    with open(temporary, "w") as output:
        json.dump(snapshot, output)

    try:
        os.remove(SNAPSHOT_FILE)
    except OSError:
        pass

    os.rename(temporary, SNAPSHOT_FILE)


def record_filesystem_changes():
    """Infer installs, removals, and replacements since the last boot."""

    previous = _load_snapshot()
    current = _root_snapshot()

    previous_names = set(previous)
    current_names = set(current)

    added = sorted(current_names - previous_names)
    removed = sorted(previous_names - current_names)
    changed = []

    for name in sorted(previous_names & current_names):
        if previous[name] != current[name]:
            changed.append(name)

    if previous:
        for name in added:
            record(
                "FILE_INSTALLED",
                "FILESYSTEM",
                "COMPLETED",
                {"path": "/" + name, "size": current[name]["size"]}
            )

        for name in removed:
            record(
                "FILE_REMOVED",
                "FILESYSTEM",
                "COMPLETED",
                {"path": "/" + name}
            )

        for name in changed:
            record(
                "FILE_CHANGED",
                "FILESYSTEM",
                "COMPLETED",
                {
                    "path": "/" + name,
                    "old_size": previous[name]["size"],
                    "new_size": current[name]["size"],
                }
            )

    else:
        record(
            "FILESYSTEM_BASELINE_CREATED",
            "FILESYSTEM",
            "COMPLETED",
            {"entries": len(current)}
        )

    try:
        _save_snapshot(current)
    except Exception as error:
        exception("activity_log.snapshot", error)

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
    }


def read(limit=100):
    try:
        with open(LOG_FILE, "r") as source:
            lines = source.readlines()
    except OSError:
        return []

    events = []

    for line in lines[-limit:]:
        try:
            events.append(json.loads(line))
        except Exception:
            pass

    return events


def clear():
    _ensure_directory()

    for path in (LOG_FILE, BACKUP_LOG):
        try:
            os.remove(path)
        except OSError:
            pass

    record("LOG_CLEARED", "LOGGING", "COMPLETED")
