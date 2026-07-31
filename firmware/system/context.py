"""KeychainOS application context and controlled service access."""

import gc


class AppContext:
    """Services supplied to every dynamic application through run(context)."""

    def __init__(
        self,
        display,
        touch,
        ui,
        config=None,
        scanner=None,
        loader=None,
        services=None,
        navigation=None,
        app_manifest=None,
    ):
        self.display = display
        self.touch = touch
        self.ui = ui
        self.config = config
        self.scanner = scanner
        self.loader = loader
        self.services = services or {}
        self.navigation = navigation
        self.app_manifest = app_manifest
        self._exit_requested = False
        self._result = None

    def service(self, name, default=None):
        """Return a named optional system service."""
        return self.services.get(name, default)

    def notify(self, title, message, level="info"):
        """Show a notification through the notification service when present."""
        notifications = self.service("notifications")
        if notifications is not None and hasattr(notifications, "show"):
            return notifications.show(title, message, level=level)
        if self.ui is not None and hasattr(self.ui, "draw_dialog"):
            return self.ui.draw_dialog(
                self.display,
                title,
                message,
                buttons=("OK",),
                danger=level in ("error", "danger"),
            )
        return None

    def request_exit(self, result="EXIT"):
        """Ask the running application to return to the launcher."""
        self._exit_requested = True
        self._result = result
        return result

    def exit_requested(self):
        return self._exit_requested

    def result(self):
        return self._result

    def navigate_back(self):
        """Return to the previous launcher screen when navigation is available."""
        if self.navigation is not None and hasattr(self.navigation, "back"):
            return self.navigation.back()
        return self.request_exit("BACK")

    def navigate_home(self):
        """Return to the Home screen when navigation is available."""
        if self.navigation is not None and hasattr(self.navigation, "home"):
            return self.navigation.home()
        return self.request_exit("HOME")

    def refresh_category(self, category_id=None):
        """Refresh a category after an app install, removal, or edit."""
        if self.scanner is None:
            return []
        if category_id is None and self.app_manifest is not None:
            category_id = self.app_manifest.get("category")
        if category_id:
            return self.scanner.refresh_category(category_id)
        return self.scanner.refresh_all()

    def app_data_directory(self):
        """Return the standard writable data directory for the active app."""
        if not self.app_manifest:
            return "/data/apps/unknown"
        package_id = str(self.app_manifest.get("id", "unknown"))
        safe = []
        for character in package_id:
            if character.isalnum() or character in (".", "_", "-"):
                safe.append(character)
            else:
                safe.append("_")
        return "/data/apps/" + "".join(safe)

    def free_memory(self):
        """Run garbage collection and return free heap memory."""
        gc.collect()
        return gc.mem_free()

    def child(self, app_manifest=None):
        """Create a context for another application using the same services."""
        return AppContext(
            display=self.display,
            touch=self.touch,
            ui=self.ui,
            config=self.config,
            scanner=self.scanner,
            loader=self.loader,
            services=self.services,
            navigation=self.navigation,
            app_manifest=app_manifest,
        )


def create_context(
    display,
    touch,
    ui,
    config=None,
    scanner=None,
    loader=None,
    services=None,
    navigation=None,
    app_manifest=None,
):
    """Create and return a standard KeychainOS application context."""
    return AppContext(
        display=display,
        touch=touch,
        ui=ui,
        config=config,
        scanner=scanner,
        loader=loader,
        services=services,
        navigation=navigation,
        app_manifest=app_manifest,
    )
