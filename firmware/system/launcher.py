"""KeychainOS dynamic launcher with event-driven redraws."""

import gc
import time

from system import bootstrap, config, error_handler, screensaver, ui
from system.app_loader import get_loader
from system.app_scanner import get_scanner
from system.context import create_context
from system.display import get_display
from system.navigation import Navigation
from system.touch import get_touch


class Launcher:
    def __init__(self):
        self.display = get_display()
        self.touch = get_touch()
        self.scanner = get_scanner()
        self.loader = get_loader()
        self.navigation = Navigation()
        self.last_input = time.ticks_ms()

    def launch(self, app):
        context = create_context(
            self.display,
            self.touch,
            ui,
            config.load(),
            self.scanner,
            self.loader,
            navigation=self.navigation,
            app_manifest=app,
        )
        try:
            return self.loader.run(app, context)
        except Exception as error:
            error_handler.show(
                self.display,
                self.touch,
                ui,
                app.get("name", "App"),
                error,
            )
        finally:
            gc.collect()

    def category(self, category):
        selected = 0
        apps = self.scanner.scan_apps(category, force=True)
        dirty = True

        while True:
            if dirty:
                ui.draw_grid(
                    self.display,
                    apps,
                    selected,
                    category["name"],
                    True,
                )
                dirty = False

            gesture = self.touch.wait_gesture(timeout_ms=250)
            if gesture is None:
                continue

            self.last_input = time.ticks_ms()
            kind = gesture["type"]

            if kind == "LEFT" and apps:
                selected = (selected + 1) % len(apps)
                dirty = True
            elif kind == "RIGHT":
                return
            elif kind == "DOWN":
                apps = self.scanner.refresh_category(category["id"])
                selected = 0
                dirty = True
            elif kind == "TAP":
                if ui.is_back_tap(gesture["x"], gesture["y"]):
                    return
                index = ui.item_at(
                    gesture["x"], gesture["y"], apps, selected
                )
                if index is not None:
                    selected = index
                    self.launch(apps[index])
                    apps = self.scanner.scan_apps(category, force=True)
                    dirty = True
            elif kind == "LONG_PRESS":
                # Long-press handling will be wired to context_menu next.
                dirty = True

    def run(self):
        bootstrap.ensure_structure()
        self.display.init()
        if not self.touch.init():
            raise RuntimeError("Touch controller not found")

        selected = 0
        categories = self.scanner.scan_categories(force=True)
        dirty = True

        while True:
            if dirty:
                ui.draw_grid(
                    self.display,
                    categories,
                    selected,
                    "KeychainOS",
                    False,
                )
                dirty = False

            settings = config.load()
            timeout_ms = int(
                settings.get("screen_timeout_seconds", 60)
            ) * 1000
            gesture = self.touch.wait_gesture(timeout_ms=250)

            if gesture is None:
                if (
                    timeout_ms > 0
                    and time.ticks_diff(
                        time.ticks_ms(), self.last_input
                    ) >= timeout_ms
                ):
                    screensaver.run(
                        self.display,
                        self.touch,
                        settings,
                    )
                    self.last_input = time.ticks_ms()
                    dirty = True
                continue

            self.last_input = time.ticks_ms()
            kind = gesture["type"]

            if kind == "LEFT" and categories:
                selected = (selected + 1) % len(categories)
                dirty = True
            elif kind == "RIGHT" and categories:
                selected = (selected - 1) % len(categories)
                dirty = True
            elif kind == "DOWN":
                categories = self.scanner.refresh_all()
                selected = 0
                dirty = True
            elif kind == "TAP":
                index = ui.item_at(
                    gesture["x"], gesture["y"], categories, selected
                )
                if index is not None:
                    selected = index
                    self.category(categories[index])
                    categories = self.scanner.scan_categories(force=True)
                    dirty = True
            elif kind == "LONG_PRESS":
                dirty = True

            gc.collect()
