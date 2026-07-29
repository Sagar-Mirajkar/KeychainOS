"""Registry-aware KeychainOS launcher with complete activity logging.

This launcher deliberately imports applications only when selected. It logs:
- Boot and startup
- Files added, removed, or changed since the previous boot
- Menu navigation
- App launches and exits
- Import failures and runtime exceptions
- Theme applications
- Soft recovery to the current menu after an app failure
"""

from machine import Pin
import gc
import sys
import time

Pin(6, Pin.OUT, value=1)

import activity_log

activity_log.record("BOOT", "SYSTEM", "STARTED")
activity_log.record_filesystem_changes()

from st7789 import ST7789
from touch import CST816D
import theme_manager
import ui

HOME_ITEMS = (
    ("FILES", "file_manager", "APP"),
    ("MEDIA", "media_browser", "APP"),
    ("APPS", None, "APPS_MENU"),
    ("GAMES", None, "GAMES_MENU"),
    ("TOOLS", None, "TOOLS_MENU"),
    ("REMOTE", None, "REMOTE_MENU"),
    ("CONNECTIONS", None, "CONNECTIONS_MENU"),
    ("DEVELOPER", None, "DEVELOPER_MENU"),
    ("SETTINGS", None, "SETTINGS_MENU"),
    ("ABOUT", None, "ABOUT_MENU"),
)

APPS_ITEMS = (
    ("NOTES", "notes"),
    ("CHECKLIST", "checklist"),
    ("TASKS", "tasks"),
    ("REMINDERS", "reminders"),
    ("HABITS", "habit_tracker"),
    ("CALENDAR", "calendar_tool"),
)

GAMES_ITEMS = (
    ("SNAKE", "snake"),
    ("TIC TAC TOE", "tic_tac_toe"),
    ("PONG", "pong"),
    ("BREAKOUT", "breakout"),
    ("2048", "game_2048"),
    ("MINESWEEPER", "minesweeper"),
    ("MEMORY MATCH", "memory_match"),
    ("LIGHTS OUT", "lights_out"),
    ("CONNECT FOUR", "connect_four"),
    ("SIMON SAYS", "simon_says"),
    ("REACTION TEST", "reaction_test"),
)

TOOLS_ITEMS = (
    ("CALCULATOR", "calculator"),
    ("CLOCK", "clock"),
    ("STOPWATCH", "stopwatch"),
    ("TIMER", "timer"),
    ("ALARM", "alarm"),
    ("POMODORO", "pomodoro"),
    ("FLASHLIGHT", "flashlight"),
    ("COUNTER", "counter"),
    ("CONVERTER", "converter"),
    ("DICE", "dice"),
    ("RANDOM", "random_number"),
    ("OHM'S LAW", "ohms_law"),
    ("RESISTOR", "resistor_calculator"),
    ("NUMBER CONVERTER", "number_converter"),
    ("MORSE", "morse_code"),
    ("METRONOME", "metronome"),
    ("GPIO REFERENCE", "gpio_reference"),
    ("I2C SCANNER", "i2c_scanner"),
    ("WI-FI SCANNER", "wifi_scanner"),
    ("SYSTEM MONITOR", "system_monitor"),
    ("PASSWORD", "password_generator"),
    ("DRAWING PAD", "drawing_pad"),
    ("NFC", "nfc_app"),
)

REMOTE_ITEMS = (
    ("COMPUTER", "computer_remote"),
    ("PRESENTATION", "presentation_remote"),
    ("MEDIA REMOTE", "media_remote"),
    ("HTTP REMOTE", "http_remote"),
    ("MQTT REMOTE", "mqtt_remote"),
    ("BLE REMOTE", "ble_remote"),
    ("USB REMOTE", "usb_remote"),
    ("IR REMOTE", "ir_remote"),
    ("MACROS", "macro_manager"),
)

CONNECTION_ITEMS = (
    ("WI-FI INFO", "wifi_info"),
    ("WI-FI SCANNER", "wifi_scanner"),
    ("BLE SCANNER", "ble_scanner"),
    ("NFC", "nfc_app"),
)

DEVELOPER_ITEMS = (
    ("DIAGNOSTICS", "diagnostics"),
    ("HARDWARE TEST", "hardware_test"),
    ("ACTIVITY LOG", "activity_viewer"),
    ("DISPLAY BENCH", "display_benchmark"),
    ("DIRTY RECT", "dirty_rect_test"),
    ("FRAMEBUFFER", "framebuffer_test"),
    ("DOUBLE BUFFER", "double_buffer_test"),
    ("SPI SPEED", "spi_speed_test"),
    ("TRANSITIONS", "transition_test"),
    ("SD BENCHMARK", "sd_benchmark"),
)

SETTINGS_ITEMS = (
    ("THEMES", "settings_themes"),
    ("BRIGHTNESS", "settings_brightness"),
    ("SCREEN TIMEOUT", "settings_screen_timeout"),
    ("DATE & TIME", "settings_date_time"),
    ("WI-FI", "settings_wifi"),
    ("TOUCH", "settings_touch"),
    ("DEVICE INFO", "settings_device_info"),
    ("SOFTWARE UPDATE", "settings_software_update"),
    ("STORAGE", "settings_storage"),
    ("RESTART", "settings_restart"),
)

ABOUT_ITEMS = (
    ("ABOUT", "about"),
    ("HARDWARE", "about_hardware"),
    ("SOFTWARE", "about_software"),
    ("DIAGNOSTICS", "diagnostics"),
)

MENUS = {
    "APPS": APPS_ITEMS,
    "GAMES": GAMES_ITEMS,
    "TOOLS": TOOLS_ITEMS,
    "REMOTE": REMOTE_ITEMS,
    "CONNECTIONS": CONNECTION_ITEMS,
    "DEVELOPER": DEVELOPER_ITEMS,
    "SETTINGS": SETTINGS_ITEMS,
    "ABOUT": ABOUT_ITEMS,
}

HOME_INDEX = 0
MENU_INDEX = 0
CURRENT_SCREEN = "HOME"
CURRENT_MENU = None

display = ST7789()
touch = CST816D()


def item_names(items):
    return tuple(item[0] for item in items)


def draw_home():
    global CURRENT_SCREEN
    global CURRENT_MENU

    CURRENT_SCREEN = "HOME"
    CURRENT_MENU = None
    ui.draw_carousel(display, item_names(HOME_ITEMS), HOME_INDEX, "KeychainOS")


def draw_menu(menu_name):
    global CURRENT_SCREEN
    global CURRENT_MENU

    CURRENT_SCREEN = "MENU"
    CURRENT_MENU = menu_name
    items = MENUS[menu_name]
    ui.draw_carousel(display, item_names(items), MENU_INDEX, menu_name.title())


def error_screen(title, error):
    activity_log.exception(title, error)
    display.fill(0xF800)
    ui.centred_text(display, title[:28], 92, 0xFFFF, 0xF800)
    ui.centred_text(display, error.__class__.__name__, 130, 0xFFFF, 0xF800)
    ui.centred_text(display, str(error)[:28], 160, 0xFFFF, 0xF800)
    ui.centred_text(display, "Tap to continue", 270, 0xFFE0, 0xF800)

    while True:
        gesture = touch.capture_gesture()
        if gesture and gesture[0] in ("TAP", "RIGHT"):
            break


def build_snake_context():
    return {
        "fill_rect": display.fill_rect,
        "fill_screen": display.fill,
        "draw_text": lambda text, x, y, colour, background, width: ui.draw_text(
            display, text, x, y, colour, background, width
        ),
        "outline_rect": display.outline_rect,
        "capture_gesture": touch.capture_gesture,
        "poll_gesture": touch.poll_gesture,
    }


def run_module(display_name, module_name):
    activity_log.app_launch(display_name, module_name)
    module = None

    try:
        gc.collect()
        module = __import__(module_name)

        if module_name == "snake":
            result = module.run(build_snake_context())

        elif module_name == "tic_tac_toe":
            result = module.run(display, touch)

        elif module_name in ("sd_benchmark",):
            result = module.benchmark()
            activity_log.record(
                "TOOL_RESULT",
                "APPLICATION",
                "COMPLETED",
                {"name": display_name, "result": result}
            )
            ui.draw_placeholder(display, display_name, "Result logged")
            time.sleep_ms(900)

        elif hasattr(module, "run"):
            result = module.run(display, touch, ui)

        else:
            raise AttributeError(module_name + " has no compatible run()")

        activity_log.app_exit(display_name, result)
        return result

    except Exception as error:
        activity_log.exception(module_name, error)
        error_screen(display_name + " ERROR", error)
        return None

    finally:
        if module_name in sys.modules:
            del sys.modules[module_name]
        module = None
        gc.collect()


def open_home_item():
    global MENU_INDEX

    name, module_name, kind = HOME_ITEMS[HOME_INDEX]
    activity_log.record(
        "HOME_ITEM_SELECTED",
        "NAVIGATION",
        "INFO",
        {"name": name, "kind": kind}
    )

    if kind == "APP":
        run_module(name, module_name)
        draw_home()
        return

    menu_name = kind.replace("_MENU", "")
    MENU_INDEX = 0
    draw_menu(menu_name)


def open_menu_item():
    name, module_name = MENUS[CURRENT_MENU][MENU_INDEX]
    run_module(name, module_name)
    draw_menu(CURRENT_MENU)


def initialize():
    activity_log.record("HARDWARE_INIT", "SYSTEM", "STARTED")

    display.init()

    if not touch.init():
        raise RuntimeError("Touch controller unavailable")

    activity_log.record(
        "HARDWARE_INIT",
        "SYSTEM",
        "COMPLETED",
        {"display": "ST7789", "touch": "CST816D"}
    )

    draw_home()
    activity_log.record("KEYCHAINOS_READY", "SYSTEM", "COMPLETED")


def run():
    global HOME_INDEX
    global MENU_INDEX

    print()
    print("================================")
    print("KeychainOS Complete Launcher")
    print("================================")

    try:
        initialize()
    except Exception as error:
        activity_log.exception("initialize", error)
        raise

    while True:
        try:
            gesture = touch.capture_gesture()

            if gesture is None:
                time.sleep_ms(10)
                continue

            kind, x, y = gesture

            if CURRENT_SCREEN == "HOME":
                if kind == "LEFT":
                    HOME_INDEX = (HOME_INDEX + 1) % len(HOME_ITEMS)
                    draw_home()

                elif kind == "RIGHT":
                    HOME_INDEX = (HOME_INDEX - 1) % len(HOME_ITEMS)
                    draw_home()

                elif kind == "TAP":
                    open_home_item()

            elif CURRENT_SCREEN == "MENU":
                items = MENUS[CURRENT_MENU]

                if kind == "TAP" and x < 70 and y < 42:
                    activity_log.record(
                        "BACK_TO_HOME",
                        "NAVIGATION",
                        "INFO",
                        {"from": CURRENT_MENU}
                    )
                    draw_home()

                elif kind == "DOWN":
                    draw_home()

                elif kind == "LEFT":
                    MENU_INDEX = (MENU_INDEX + 1) % len(items)
                    draw_menu(CURRENT_MENU)

                elif kind == "RIGHT":
                    MENU_INDEX = (MENU_INDEX - 1) % len(items)
                    draw_menu(CURRENT_MENU)

                elif kind == "TAP":
                    open_menu_item()

        except KeyboardInterrupt:
            activity_log.record("REPL_INTERRUPT", "SYSTEM", "COMPLETED")
            raise

        except Exception as error:
            activity_log.exception("main_loop", error)
            error_screen("SYSTEM ERROR", error)
            draw_home()


run()
