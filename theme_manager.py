"""KeychainOS theme loader and persistent theme selection."""

import os

DEFAULT_THEME = "minimal_light"
SETTINGS_FILE = "/theme.cfg"

THEMES = (
    "minimal_light",
    "dark_modern",
    "pastel_rounded",
    "glassy_blur",
    "retro_pixel",
    "compact_clean",
)


def is_valid_theme(theme_name):
    return theme_name in THEMES


def save_theme(theme_name):
    if not is_valid_theme(theme_name):
        raise ValueError("Unknown theme: " + str(theme_name))

    temporary_file = SETTINGS_FILE + ".new"

    with open(temporary_file, "w") as output:
        output.write(theme_name)

    try:
        os.remove(SETTINGS_FILE)
    except OSError:
        pass

    os.rename(temporary_file, SETTINGS_FILE)
    print("Theme saved:", theme_name)


def load_saved_name():
    try:
        with open(SETTINGS_FILE, "r") as source:
            theme_name = source.read().strip()

        if is_valid_theme(theme_name):
            return theme_name

    except OSError:
        pass

    return DEFAULT_THEME


def load_theme(theme_name=None):
    if theme_name is None:
        theme_name = load_saved_name()

    if not is_valid_theme(theme_name):
        theme_name = DEFAULT_THEME

    module_name = "theme_" + theme_name
    theme_module = __import__(module_name)

    print("Theme loaded:", theme_name)
    return theme_module


def next_theme(current_name):
    if not is_valid_theme(current_name):
        return DEFAULT_THEME

    position = THEMES.index(current_name)
    return THEMES[(position + 1) % len(THEMES)]


def previous_theme(current_name):
    if not is_valid_theme(current_name):
        return DEFAULT_THEME

    position = THEMES.index(current_name)
    return THEMES[(position - 1) % len(THEMES)]
