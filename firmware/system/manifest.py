"""KeychainOS application and theme manifest validator."""

import json
import os

SUPPORTED_FORMAT = 1
SUPPORTED_RUNTIMES = (
    "micropython",
    "native",
    "declarative",
    "theme",
)

REQUIRED_APP_FIELDS = (
    "format",
    "id",
    "name",
    "version",
    "category",
    "runtime",
    "entry",
)

VALID_PERMISSIONS = (
    "display",
    "touch",
    "time",
    "notifications",
    "network",
    "ble",
    "nfc",
    "usb",
    "files.internal.read",
    "files.internal.write",
    "files.sd.read",
    "files.sd.write",
    "system.info",
    "system.settings",
    "remote.commands",
)


class ManifestError(Exception):
    """Raised when a KeychainOS manifest is invalid."""


def exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def join_path(folder, name):
    if folder == "/":
        return "/" + name
    return folder.rstrip("/") + "/" + name


def safe_identifier(value):
    """Return True for a safe package or category identifier."""
    if not isinstance(value, str) or not value:
        return False
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    return all(character in allowed for character in value)


def load_json(path):
    """Read and return a JSON object."""
    try:
        with open(path, "r") as stream:
            value = json.load(stream)
    except Exception as error:
        raise ManifestError("Cannot read JSON: %s" % error)
    if not isinstance(value, dict):
        raise ManifestError("Manifest root must be an object")
    return value


def validate_permissions(permissions):
    """Validate a manifest permission list."""
    if permissions is None:
        return []
    if not isinstance(permissions, list):
        raise ManifestError("permissions must be a list")
    result = []
    for permission in permissions:
        if permission not in VALID_PERMISSIONS:
            raise ManifestError("Unknown permission: %s" % permission)
        if permission not in result:
            result.append(permission)
    return result


def validate_dependencies(dependencies):
    """Validate dependency entries and return a normalized list."""
    if dependencies is None:
        return []
    if not isinstance(dependencies, list):
        raise ManifestError("dependencies must be a list")
    result = []
    for dependency in dependencies:
        if isinstance(dependency, str):
            dependency = {"id": dependency, "minimum_version": "0.0.0"}
        if not isinstance(dependency, dict):
            raise ManifestError("Invalid dependency entry")
        package_id = dependency.get("id")
        if not safe_identifier(package_id):
            raise ManifestError("Invalid dependency id")
        result.append({
            "id": package_id,
            "minimum_version": str(dependency.get("minimum_version", "0.0.0")),
        })
    return result


def validate_app_manifest(data, folder=None):
    """Validate and normalize an application manifest."""
    if not isinstance(data, dict):
        raise ManifestError("Manifest must be an object")

    for field in REQUIRED_APP_FIELDS:
        if field not in data:
            raise ManifestError("Missing field: %s" % field)

    if data.get("format") != SUPPORTED_FORMAT:
        raise ManifestError("Unsupported manifest format")

    package_id = data.get("id")
    category = data.get("category")
    runtime = data.get("runtime")
    entry = data.get("entry")

    if not safe_identifier(package_id):
        raise ManifestError("Invalid package id")
    if not safe_identifier(category):
        raise ManifestError("Invalid category id")
    if runtime not in SUPPORTED_RUNTIMES:
        raise ManifestError("Unsupported runtime: %s" % runtime)
    if not isinstance(entry, str) or not entry:
        raise ManifestError("Invalid entry")
    if entry.startswith("/") or ".." in entry.split("/"):
        raise ManifestError("Entry must remain inside app folder")

    if folder is not None:
        entry_path = join_path(folder, entry)
        if runtime == "micropython" and not exists(entry_path):
            raise ManifestError("Missing entry file: %s" % entry)

    name = str(data.get("name", "")).strip()
    if not name:
        raise ManifestError("App name cannot be empty")

    normalized = dict(data)
    normalized["name"] = name
    normalized["version"] = str(data.get("version"))
    normalized["enabled"] = bool(data.get("enabled", True))
    normalized["order"] = int(data.get("order", 100))
    normalized["permissions"] = validate_permissions(data.get("permissions"))
    normalized["dependencies"] = validate_dependencies(data.get("dependencies"))
    normalized["icon"] = data.get("icon")
    normalized["description"] = str(data.get("description", ""))
    normalized["author"] = str(data.get("author", ""))
    normalized["minimum_os"] = str(data.get("minimum_os", "0.1.0"))
    if folder is not None:
        normalized["folder"] = folder
        normalized["entry_path"] = join_path(folder, entry)
    return normalized


def load_app_manifest(folder):
    """Load, validate, and normalize manifest.json from an app folder."""
    path = join_path(folder, "manifest.json")
    if not exists(path):
        raise ManifestError("manifest.json not found")
    return validate_app_manifest(load_json(path), folder)


def validate_category(data, folder=None):
    """Validate and normalize category.json data."""
    if not isinstance(data, dict):
        raise ManifestError("Category metadata must be an object")
    if data.get("format") != SUPPORTED_FORMAT:
        raise ManifestError("Unsupported category format")
    category_id = data.get("id")
    if not safe_identifier(category_id):
        raise ManifestError("Invalid category id")
    name = str(data.get("name", "")).strip()
    if not name:
        raise ManifestError("Category name cannot be empty")
    result = dict(data)
    result["name"] = name
    result["order"] = int(data.get("order", 100))
    result["enabled"] = bool(data.get("enabled", True))
    result["icon"] = data.get("icon")
    if folder is not None:
        result["folder"] = folder
    return result


def load_category(folder):
    """Load and validate category.json from a category folder."""
    path = join_path(folder, "category.json")
    if not exists(path):
        raise ManifestError("category.json not found")
    return validate_category(load_json(path), folder)


def compile_entry(manifest):
    """Compile a MicroPython app entry without executing it."""
    if manifest.get("runtime") != "micropython":
        return True
    path = manifest.get("entry_path")
    if not path:
        raise ManifestError("Entry path is unavailable")
    try:
        with open(path, "r") as stream:
            source = stream.read()
        compile(source, path, "exec")
        return True
    except Exception as error:
        raise ManifestError("Entry syntax error: %s" % error)
