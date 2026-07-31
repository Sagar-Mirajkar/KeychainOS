"""KeychainOS dynamic category and application scanner.

The scanner reads /apps at runtime. New app folders appear when a category is
reopened or refreshed, without changing main.py or restarting the device.
"""

import gc
import os

from system.manifest import (
    ManifestError,
    compile_entry,
    exists,
    join_path,
    load_app_manifest,
    load_category,
)

APPS_ROOT = "/apps"
MANIFEST_NAME = "manifest.json"
CATEGORY_NAME = "category.json"


class AppScanner:
    """Discover categories and applications from the writable filesystem."""

    def __init__(self, apps_root=APPS_ROOT):
        self.apps_root = apps_root.rstrip("/") or "/apps"
        self.category_cache = None
        self.app_cache = {}
        self.issues = []

    @staticmethod
    def _is_directory(path):
        """Return True when path is a directory."""
        try:
            mode = os.stat(path)[0]
            return (mode & 0x4000) != 0
        except OSError:
            return False

    @staticmethod
    def _safe_listdir(path):
        """Return a sorted directory listing, or an empty list on failure."""
        try:
            return sorted(os.listdir(path))
        except OSError:
            return []

    def _record_issue(self, issue_type, path, error):
        """Record a scanner issue without stopping the launcher."""
        issue = {
            "type": str(issue_type),
            "path": str(path),
            "error": str(error),
        }
        self.issues.append(issue)
        if len(self.issues) > 100:
            self.issues = self.issues[-100:]

    def clear_issues(self):
        self.issues = []

    def get_issues(self):
        return list(self.issues)

    def scan_categories(self, force=False):
        """Return enabled category metadata sorted by order and name."""
        if self.category_cache is not None and not force:
            return list(self.category_cache)

        categories = []
        if not exists(self.apps_root):
            self.category_cache = categories
            return categories

        for name in self._safe_listdir(self.apps_root):
            folder = join_path(self.apps_root, name)
            if not self._is_directory(folder):
                continue
            metadata_path = join_path(folder, CATEGORY_NAME)
            if not exists(metadata_path):
                continue
            try:
                category = load_category(folder)
                if category.get("enabled", True):
                    categories.append(category)
            except Exception as error:
                self._record_issue("category", folder, error)

        categories.sort(
            key=lambda item: (
                int(item.get("order", 100)),
                str(item.get("name", "")).lower(),
            )
        )
        self.category_cache = categories
        return list(categories)

    def category_by_id(self, category_id, force=False):
        """Return one category by stable ID, or None."""
        for category in self.scan_categories(force=force):
            if category.get("id") == category_id:
                return category
        return None

    def scan_apps(self, category, force=True, compile_python=True):
        """Return valid enabled apps inside one category.

        category may be a category ID string or a category metadata dictionary.
        By default the folder is rescanned every time, enabling no-reboot app
        discovery when a category is opened again.
        """
        if isinstance(category, dict):
            category_id = category.get("id")
            folder = category.get("folder")
        else:
            category_id = str(category)
            metadata = self.category_by_id(category_id, force=False)
            folder = metadata.get("folder") if metadata else None

        if not category_id:
            return []
        if not folder:
            folder = join_path(self.apps_root, category_id)

        if not force and category_id in self.app_cache:
            return list(self.app_cache[category_id])

        apps = []
        for name in self._safe_listdir(folder):
            if name == CATEGORY_NAME or name.startswith("."):
                continue
            app_folder = join_path(folder, name)
            if not self._is_directory(app_folder):
                continue
            manifest_path = join_path(app_folder, MANIFEST_NAME)
            if not exists(manifest_path):
                continue

            try:
                app = load_app_manifest(app_folder)
                if app.get("category") != category_id:
                    raise ManifestError(
                        "Manifest category %s does not match folder %s"
                        % (app.get("category"), category_id)
                    )
                if not app.get("enabled", True):
                    continue
                if compile_python and app.get("runtime") == "micropython":
                    compile_entry(app)
                app["broken"] = False
                apps.append(app)
            except Exception as error:
                self._record_issue("app", app_folder, error)

        apps.sort(
            key=lambda item: (
                int(item.get("order", 100)),
                str(item.get("name", "")).lower(),
            )
        )
        self.app_cache[category_id] = apps
        gc.collect()
        return list(apps)

    def app_by_id(self, package_id, category_id=None, force=True):
        """Find an application by package ID."""
        if category_id is not None:
            categories = [self.category_by_id(category_id, force=False)]
        else:
            categories = self.scan_categories(force=False)

        for category in categories:
            if not category:
                continue
            for app in self.scan_apps(category, force=force):
                if app.get("id") == package_id:
                    return app
        return None

    def refresh_category(self, category_id):
        """Clear and rescan one category."""
        self.app_cache.pop(category_id, None)
        return self.scan_apps(category_id, force=True)

    def refresh_all(self):
        """Clear all caches and rescan the category list."""
        self.category_cache = None
        self.app_cache = {}
        gc.collect()
        return self.scan_categories(force=True)

    def inventory(self, compile_python=False):
        """Return a complete category and app inventory."""
        inventory = []
        for category in self.scan_categories(force=True):
            inventory.append({
                "category": category,
                "apps": self.scan_apps(
                    category,
                    force=True,
                    compile_python=compile_python,
                ),
            })
        return inventory


_default_scanner = None


def get_scanner():
    """Return the shared KeychainOS scanner instance."""
    global _default_scanner
    if _default_scanner is None:
        _default_scanner = AppScanner()
    return _default_scanner
