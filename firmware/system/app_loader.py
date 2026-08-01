"""KeychainOS MicroPython-safe lazy application loader."""

import gc


class AppLoadError(Exception):
    """Raised when an application cannot be loaded or executed."""


class AppLoader:
    """Load apps with exec(), avoiding CPython-only importlib APIs."""

    def __init__(self):
        self.active_app = None
        self.active_namespace = None

    @staticmethod
    def load_namespace(manifest):
        if manifest.get("runtime") != "micropython":
            raise AppLoadError(
                "Unsupported runtime: %s" % manifest.get("runtime")
            )

        source_path = manifest.get("entry_path")
        if not source_path:
            raise AppLoadError("Application entry path is missing")

        try:
            with open(source_path, "r") as stream:
                source = stream.read()
            namespace = {
                "__name__": "keychain_dynamic_app",
                "__file__": source_path,
            }
            exec(compile(source, source_path, "exec"), namespace)
        except Exception as error:
            raise AppLoadError("Import failed: %s" % error)

        run_function = namespace.get("run")
        if not callable(run_function):
            raise AppLoadError("Application must provide run(context)")
        return namespace

    def load(self, manifest):
        self.unload()
        namespace = self.load_namespace(manifest)
        self.active_app = manifest
        self.active_namespace = namespace
        return namespace

    def run(self, manifest, context):
        namespace = None
        try:
            namespace = self.load(manifest)
            return namespace["run"](context)
        except AppLoadError:
            raise
        except Exception as error:
            raise AppLoadError("Application failed: %s" % error)
        finally:
            if namespace is not None:
                close_function = namespace.get("on_close")
                if callable(close_function):
                    try:
                        close_function()
                    except Exception:
                        pass
            self.unload()

    def unload(self, module_name=None):
        self.active_namespace = None
        self.active_app = None
        gc.collect()

    def is_running(self):
        return self.active_app is not None

    def active_manifest(self):
        return self.active_app


_default_loader = None


def get_loader():
    global _default_loader
    if _default_loader is None:
        _default_loader = AppLoader()
    return _default_loader
