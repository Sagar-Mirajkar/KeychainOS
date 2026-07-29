"""KeychainOS ESP filesystem inspector.

Upload this file to the ESP root as /esp_inspector.py, then run:

    import esp_inspector

The script prints:
- A recursive filesystem tree
- File sizes
- Contents of text/source files
- Python syntax-check results

Sensitive credential files are listed but their contents are redacted.
"""

import os

SENSITIVE_NAMES = (
    "wifi_secrets.py",
    "secrets.py",
    "credentials.py",
)

TEXT_EXTENSIONS = (
    ".py",
    ".txt",
    ".json",
    ".md",
    ".cfg",
    ".ini",
)

MAX_CONTENT_BYTES = 40000


def join_path(folder, name):
    if folder == "/":
        return "/" + name
    return folder + "/" + name


def is_directory(path):
    try:
        mode = os.stat(path)[0]
        return (mode & 0x4000) != 0
    except OSError:
        return False


def is_sensitive(path):
    name = path.rsplit("/", 1)[-1].lower()
    return name in SENSITIVE_NAMES


def is_text_file(path):
    lower_path = path.lower()
    for extension in TEXT_EXTENSIONS:
        if lower_path.endswith(extension):
            return True
    return False


def collect_files(folder, files):
    try:
        names = sorted(os.listdir(folder))
    except Exception as error:
        print("CANNOT READ DIRECTORY:", folder, repr(error))
        return

    for name in names:
        path = join_path(folder, name)

        if is_directory(path):
            print("DIR :", path)
            collect_files(path, files)
        else:
            try:
                size = os.stat(path)[6]
            except Exception:
                size = -1

            print("FILE:", path, "SIZE:", size)
            files.append((path, size))


def inspect_file(path, size):
    print()
    print("=" * 60)
    print("FILE:", path)
    print("SIZE:", size)
    print("=" * 60)

    if is_sensitive(path):
        print("[CONTENT REDACTED: SENSITIVE FILE]")
        return

    if not is_text_file(path):
        print("[CONTENT SKIPPED: NON-TEXT FILE]")
        return

    if size > MAX_CONTENT_BYTES:
        print("[CONTENT SKIPPED: FILE EXCEEDS SIZE LIMIT]")
        return

    try:
        with open(path, "r") as source_file:
            source = source_file.read()
    except Exception as error:
        print("[CANNOT READ AS TEXT]")
        print(repr(error))
        return

    print(source)

    if path.lower().endswith(".py"):
        try:
            compile(source, path, "exec")
            print()
            print("[PYTHON SYNTAX: OK]")
        except Exception as error:
            print()
            print("[PYTHON SYNTAX: ERROR]")
            print(repr(error))


def run():
    files = []

    print()
    print("############################################################")
    print("KEYCHAINOS ESP FILESYSTEM INSPECTION")
    print("############################################################")

    print()
    print("FILESYSTEM TREE")
    print("----------------")

    collect_files("/", files)

    print()
    print("############################################################")
    print("FILE CONTENTS")
    print("############################################################")

    for path, size in sorted(files):
        inspect_file(path, size)

    print()
    print("############################################################")
    print("INSPECTION COMPLETE")
    print("############################################################")


run()
