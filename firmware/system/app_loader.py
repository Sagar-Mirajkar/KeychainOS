"""KeychainOS lazy MicroPython application loader.

Applications are imported only when opened, then unloaded after exit to reduce
RAM usage and allow updated app files to be loaded without rebooting.
"""

import gc
import sys


class AppLoadError(Exception):
    """Raised when an application cannot be loaded or executed."""


class AppLoader:
    """Load, run, and unload dynamic KeychainOS applications."""

    def __init__(self):
        self.active_app = None
        self.active_module_name = None

    @staticmethod
    def _module_name(manifest):
        """Generate a unique import name from the package ID."""
        package_id = str(manifest.get("id", "application"))
        safe = []
        for character in package_id:
            if character.isalnum() or character == "_":
                safe.append(character)
            else:
                safe.append("_")
        return "keychain_app_" + "".join(safe)

    @staticmethod
    def _load_source_module(module_name, source_path):
        """Load a Python source file under a unique module name."""
        try:
            import importlib.util

            specification = importlib.util.spec_from_file_location(
                module_name,
                source_path,
            )
            if specification is None or specification.loader is None:
                raise AppLoadError("Cannot create module specification")
            module = importlib.util.module_from_spec(specification)
            sys.modules[module_name] = module
            specification.loader.exec_module(module)
            return module

        except (ImportError, AttributeError):
            # MicroPython fallback without CPython's importlib.util.
            with open(source_path, "r") as stream:
                source = stream.read()
            module_globals = {
                "__name__": module_name,
                "__file__": source_path,
                "__package__": None,
            }
            exec(compile(source, source_path, "exec"), module_globals)

            class DynamicModule:
                pass

            module = DynamicModule()
            for key, value in module_globals.items():
                setattr(module, key, value)
            sys.modules[module_name] = module
            return module

    def load(self, manifest):
        """Load one MicroPython app from normalized manifest metadata."""
        if manifest.get("runtime") != "micropython":
            raise AppLoadError(
                "Unsupported runtime: %s" % manifest.get("runtime")
            )

        source_path = manifest.get("entry_path")
        if not source_path:
            raise AppLoadError("Application entry path is missing")

        module_name = self._module_name(manifest)
        self.unload(module_name)

        try:
            module = self._load_source_module(module_name, source_path)
        except Exception as error:
            self.unload(module_name)
            raise AppLoadError("Import failed: %s" % error)

        if not hasattr(module, "run"):
            self.unload(module_name)
            raise AppLoadError("Application must provide run(context)")

        self.active_app = manifest
        self.active_module_name = module_name
        return module

    def run(self, manifest, context):
        """Load an app, call run(context), then unload it safely."""
        module = None
        module_name = self._module_name(manifest)
        try:
            module = self.load(manifest)
            result = module.run(context)
            return result
        except AppLoadError:
            raise
        except Exception as error:
            raise AppLoadError("Application failed: %s" % error)
        finally:
            try:
                if module is not None and hasattr(module, "on_close"):
                    module.on_close()
            except Exception:
                pass
            self.unload(module_name)
            self.active_app = None
            self.active_module_name = None
            gc.collect()

    def unload(self, module_name=None):
        """Remove a dynamic app module from the import cache."""
        if module_name is None:
            module_name = self.active_module_name
        if module_name and module_name in sys.modules:
            del sys.modules[module_name]
        gc.collect()

    def is_running(self):
        return self.active_app is not None

    def active_manifest(self):
        return self.active_app


_default_loader = None


def get_loader():
    """Return the shared KeychainOS application loader."""
    global _default_loader
    if _default_loader is None:
        _default_loader = AppLoader()
    return _default_loader
