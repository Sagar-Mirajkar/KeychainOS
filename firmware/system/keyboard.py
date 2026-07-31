"""KeychainOS thumb-friendly on-screen keyboard.

The keyboard uses eight large character keys per page instead of a cramped
QWERTY layout. It supports text, password, numeric, and filename input.
"""

from system.ui import (
    PAPER,
    INK,
    MUTED,
    BORDER,
    CARD,
    CARD_SELECTED,
    TEAL_DARK,
    SOFT_RED,
    draw_header,
)

WIDTH = 240
HEIGHT = 320

CHARACTER_PAGES = (
    "abcdefgh",
    "ijklmnop",
    "qrstuvwx",
    "yz012345",
    "6789.-_@",
    "!#$%&*+/",
    "=:;?,()",
    "[]{}<>\\",
)

NUMERIC_PAGES = (
    "12345678",
    "90.-+*/=",
)

KEY_X = 6
KEY_Y = 92
KEY_WIDTH = 53
KEY_HEIGHT = 46
KEY_GAP_X = 6
KEY_GAP_Y = 7

CONTROL_Y = 204
CONTROL_HEIGHT = 43
ACTION_Y = 262
ACTION_HEIGHT = 48


def _inside(x, y, rect):
    rx, ry, width, height = rect
    return rx <= x < rx + width and ry <= y < ry + height


def _draw_button(display, rect, label, selected=False, danger=False):
    x, y, width, height = rect
    background = CARD_SELECTED if selected else CARD
    border = SOFT_RED if danger else (TEAL_DARK if selected else BORDER)
    display.fill_rect(x, y, width, height, background)
    display.outline_rect(x, y, width, height, border, 2 if selected else 1)
    label = str(label)
    maximum = max(1, (width - 6) // 8)
    if len(label) > maximum:
        label = label[:maximum]
    text_width = max(8, len(label) * 8)
    display.draw_text(
        label,
        x + (width - text_width) // 2,
        y + (height - 16) // 2,
        INK,
        background,
        text_width,
    )


def _character_rect(index):
    column = index % 4
    row = index // 4
    return (
        KEY_X + column * (KEY_WIDTH + KEY_GAP_X),
        KEY_Y + row * (KEY_HEIGHT + KEY_GAP_Y),
        KEY_WIDTH,
        KEY_HEIGHT,
    )


def _gesture_point(touch):
    gesture = touch.capture_gesture()
    if gesture is None:
        return None
    if isinstance(gesture, dict):
        return gesture.get("type"), gesture.get("x"), gesture.get("y")
    return gesture


def input_text(
    display,
    touch,
    title="Keyboard",
    initial="",
    password=False,
    numeric=False,
    maximum_length=64,
    action_label="DONE",
):
    """Show the keyboard and return entered text, or None when cancelled."""

    value = str(initial)
    page_index = 0
    uppercase = False
    reveal_password = False
    pages = NUMERIC_PAGES if numeric else CHARACTER_PAGES

    shift_rect = (6, CONTROL_Y, 52, CONTROL_HEIGHT)
    page_rect = (64, CONTROL_Y, 52, CONTROL_HEIGHT)
    space_rect = (122, CONTROL_Y, 54, CONTROL_HEIGHT)
    delete_rect = (182, CONTROL_Y, 52, CONTROL_HEIGHT)
    cancel_rect = (6, ACTION_Y, 82, ACTION_HEIGHT)
    action_rect = (96, ACTION_Y, 138, ACTION_HEIGHT)
    reveal_rect = (184, 50, 50, 32)

    while True:
        display.fill(PAPER)
        draw_header(display, title, False)

        display.fill_rect(6, 48, 172 if password else 228, 36, CARD_SELECTED)
        display.outline_rect(6, 48, 172 if password else 228, 36, BORDER, 1)

        visible = value
        if password and not reveal_password:
            visible = "*" * len(value)
        visible = visible[-20:]
        display.draw_text(visible, 12, 58, INK, CARD_SELECTED, 160 if password else 216)

        if password:
            _draw_button(display, reveal_rect, "SHOW" if not reveal_password else "HIDE")

        characters = pages[page_index]
        if uppercase and not numeric:
            characters = characters.upper()

        for index, character in enumerate(characters):
            _draw_button(display, _character_rect(index), character)

        if numeric:
            _draw_button(display, shift_rect, "123", True)
        else:
            _draw_button(display, shift_rect, "ABC" if uppercase else "abc", uppercase)

        _draw_button(display, page_rect, "PAGE")
        _draw_button(display, space_rect, "SPACE")
        _draw_button(display, delete_rect, "DEL")
        _draw_button(display, cancel_rect, "CANCEL", danger=True)
        _draw_button(display, action_rect, action_label, selected=True)

        display.draw_text(
            "%d/%d" % (page_index + 1, len(pages)),
            92,
            86,
            MUTED,
            PAPER,
            56,
        )

        event = _gesture_point(touch)
        if event is None:
            continue
        kind, x, y = event

        if kind == "LONG_PRESS" and _inside(x, y, delete_rect):
            value = ""
            continue
        if kind != "TAP":
            continue

        if password and _inside(x, y, reveal_rect):
            reveal_password = not reveal_password
            continue

        handled = False
        for index, character in enumerate(characters):
            if _inside(x, y, _character_rect(index)):
                if len(value) < maximum_length:
                    value += character
                handled = True
                break
        if handled:
            continue

        if _inside(x, y, shift_rect):
            if not numeric:
                uppercase = not uppercase
        elif _inside(x, y, page_rect):
            page_index = (page_index + 1) % len(pages)
        elif _inside(x, y, space_rect):
            if len(value) < maximum_length:
                value += " "
        elif _inside(x, y, delete_rect):
            value = value[:-1]
        elif _inside(x, y, cancel_rect):
            return None
        elif _inside(x, y, action_rect):
            return value


def input_password(display, touch, title="Password", maximum_length=64):
    """Show a password keyboard and return the entered password."""
    return input_text(
        display,
        touch,
        title=title,
        password=True,
        maximum_length=maximum_length,
        action_label="CONNECT",
    )


def input_number(display, touch, title="Number", initial="", maximum_length=20):
    """Show a numeric keyboard and return the entered value as text."""
    return input_text(
        display,
        touch,
        title=title,
        initial=initial,
        numeric=True,
        maximum_length=maximum_length,
        action_label="DONE",
    )
