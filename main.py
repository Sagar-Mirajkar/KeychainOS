"""KeychainOS launcher with Themes, Games, and Tools."""

from machine import Pin
import gc
import time

Pin(6, Pin.OUT, value=1)

from st7789 import ST7789
from touch import CST816D
import theme_manager
import ui
import snake
import tic_tac_toe
import calculator
import clock

HOME_APPS = (
    "FILES",
    "GAMES",
    "TOOLS",
    "NOTES",
    "SETTINGS"
)

GAME_APPS = (
    "SNAKE",
    "TIC TAC TOE"
)

TOOL_APPS = (
    "CALCULATOR",
    "CLOCK"
)

home_index = 0
games_index = 0
tools_index = 0
theme_index = 0
screen_mode = "HOME"

display = ST7789()
touch = CST816D()


def find_saved_theme_index():
    saved_name = theme_manager.load_saved_name()

    try:
        return theme_manager.THEMES.index(saved_name)
    except ValueError:
        return 0


def draw_home():
    global screen_mode
    screen_mode = "HOME"
    ui.draw_carousel(display, HOME_APPS, home_index, "KeychainOS")


def draw_games():
    global screen_mode
    screen_mode = "GAMES"
    ui.draw_carousel(display, GAME_APPS, games_index, "Games")


def draw_tools():
    global screen_mode
    screen_mode = "TOOLS"
    ui.draw_carousel(display, TOOL_APPS, tools_index, "Tools")


def draw_themes():
    global screen_mode
    screen_mode = "THEMES"
    ui.draw_theme_settings(display, theme_index)


def show_placeholder(title, message):
    global screen_mode
    screen_mode = "PLACEHOLDER"
    ui.draw_placeholder(display, title, message)


def build_snake_context():
    return {
        "fill_rect": display.fill_rect,
        "fill_screen": display.fill,
        "draw_text": lambda text, x, y, colour, background, width: ui.draw_text(
            display, text, x, y, colour, background, width
        ),
        "outline_rect": display.outline_rect,
        "capture_gesture": touch.capture_gesture,
        "poll_gesture": touch.poll_gesture
    }


def open_home_app():
    global theme_index
    selected = HOME_APPS[home_index]

    if selected == "FILES":
        show_placeholder("FILES", "SD support postponed")
    elif selected == "GAMES":
        draw_games()
    elif selected == "TOOLS":
        draw_tools()
    elif selected == "NOTES":
        show_placeholder("NOTES", "Coming later")
    elif selected == "SETTINGS":
        theme_index = find_saved_theme_index()
        draw_themes()


def open_game():
    selected = GAME_APPS[games_index]

    if selected == "SNAKE":
        snake.run(build_snake_context())
    elif selected == "TIC TAC TOE":
        tic_tac_toe.run(display, touch)

    draw_games()


def open_tool():
    selected = TOOL_APPS[tools_index]

    if selected == "CALCULATOR":
        calculator.run(display, touch, ui)
    elif selected == "CLOCK":
        clock.run(display, touch, ui)

    draw_tools()


def apply_selected_theme():
    selected_name = theme_manager.THEMES[theme_index]
    ui.set_theme(selected_name, save=True)
    print("Applied theme:", ui.get_theme_display_name())
    ui.draw_placeholder(display, "SETTINGS", "Theme applied")
    time.sleep_ms(700)
    draw_home()


def initialize():
    global theme_index

    print()
    print("================================")
    print("KeychainOS Tools Launcher")
    print("================================")

    gc.collect()
    print("Free memory:", gc.mem_free())

    display.init()

    if not touch.init():
        display.fill(0xF800)
        print("Touch controller not found")
        while True:
            time.sleep(1)

    theme_index = find_saved_theme_index()
    print("Active theme:", ui.get_theme_display_name())
    draw_home()
    print("KeychainOS ready")


def run():
    global home_index
    global games_index
    global tools_index
    global theme_index

    initialize()

    while True:
        gesture = touch.capture_gesture()

        if gesture is None:
            time.sleep_ms(10)
            continue

        kind, x, y = gesture

        if screen_mode == "HOME":
            if kind == "LEFT":
                home_index = (home_index + 1) % len(HOME_APPS)
                draw_home()
            elif kind == "RIGHT":
                home_index = (home_index - 1) % len(HOME_APPS)
                draw_home()
            elif kind == "TAP":
                open_home_app()

        elif screen_mode == "GAMES":
            if kind == "TAP" and x < 70 and y < 38:
                draw_home()
            elif kind == "LEFT":
                games_index = (games_index + 1) % len(GAME_APPS)
                draw_games()
            elif kind == "RIGHT":
                games_index = (games_index - 1) % len(GAME_APPS)
                draw_games()
            elif kind == "DOWN":
                draw_home()
            elif kind == "TAP":
                open_game()

        elif screen_mode == "TOOLS":
            if kind == "TAP" and x < 70 and y < 38:
                draw_home()
            elif kind == "LEFT":
                tools_index = (tools_index + 1) % len(TOOL_APPS)
                draw_tools()
            elif kind == "RIGHT":
                tools_index = (tools_index - 1) % len(TOOL_APPS)
                draw_tools()
            elif kind == "DOWN":
                draw_home()
            elif kind == "TAP":
                open_tool()

        elif screen_mode == "THEMES":
            if kind == "TAP" and x < 70 and y < 38:
                theme_index = find_saved_theme_index()
                draw_home()
            elif kind == "LEFT":
                theme_index = (theme_index + 1) % len(theme_manager.THEMES)
                draw_themes()
            elif kind == "RIGHT":
                theme_index = (theme_index - 1) % len(theme_manager.THEMES)
                draw_themes()
            elif kind == "TAP":
                apply_selected_theme()
            elif kind == "DOWN":
                theme_index = find_saved_theme_index()
                draw_home()

        elif screen_mode == "PLACEHOLDER":
            if kind == "RIGHT":
                draw_home()
            elif kind == "TAP" and x < 70 and y < 45:
                draw_home()


run()
