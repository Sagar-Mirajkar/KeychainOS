"""Touch calculator tool for KeychainOS."""

import time

NAME = "CALCULATOR"

BLACK = 0x0000
WHITE = 0xFFFF
BLUE = 0x001F
CYAN = 0x07FF
YELLOW = 0xFFE0
RED = 0xF800
DARK = 0x0841
PANEL = 0x18E3
BUTTON = 0x3186
OPERATOR = 0x021F
EQUALS = 0x04A0

SCREEN_X = 10
SCREEN_Y = 42
SCREEN_W = 220
SCREEN_H = 50

GRID_X = 10
GRID_Y = 102
CELL_W = 55
CELL_H = 48

BUTTONS = (
    ("7", "8", "9", "/"),
    ("4", "5", "6", "*"),
    ("1", "2", "3", "-"),
    ("C", "0", "=", "+"),
)


def safe_number_text(value):
    if isinstance(value, float):
        if value == int(value):
            value = int(value)

    text = str(value)

    if len(text) > 24:
        text = text[:24]

    return text


def calculate(left, operator, right):
    a = float(left)
    b = float(right)

    if operator == "+":
        return a + b

    if operator == "-":
        return a - b

    if operator == "*":
        return a * b

    if operator == "/":
        if b == 0:
            raise ValueError("DIV ZERO")
        return a / b

    return b


def draw_screen(display, ui, display_text, status_text="Tap buttons"):
    display.fill(DARK)
    display.fill_rect(0, 0, 240, 32, BLUE)
    ui.draw_text(display, "< CALCULATOR", 8, 7, WHITE, BLUE, 120)

    display.fill_rect(SCREEN_X, SCREEN_Y, SCREEN_W, SCREEN_H, BLACK)
    display.outline_rect(SCREEN_X, SCREEN_Y, SCREEN_W, SCREEN_H, CYAN, 2)

    trimmed = display_text[-24:]
    text_width = max(8, len(trimmed) * 8)
    text_x = SCREEN_X + SCREEN_W - text_width - 8
    ui.draw_text(display, trimmed, text_x, SCREEN_Y + 16,
                 WHITE, BLACK, text_width)

    for row in range(4):
        for column in range(4):
            label = BUTTONS[row][column]
            x = GRID_X + column * CELL_W
            y = GRID_Y + row * CELL_H

            if label in ("+", "-", "*", "/"):
                colour = OPERATOR
            elif label == "=":
                colour = EQUALS
            elif label == "C":
                colour = RED
            else:
                colour = BUTTON

            display.fill_rect(x + 2, y + 2, CELL_W - 4, CELL_H - 4, colour)
            display.outline_rect(x + 2, y + 2,
                                 CELL_W - 4, CELL_H - 4, WHITE, 1)

            label_x = x + (CELL_W - len(label) * 8) // 2
            ui.draw_text(display, label, label_x, y + 17,
                         WHITE, colour, len(label) * 8)

    ui.centred_text(display, status_text, 298, YELLOW, DARK)


def button_at(x, y):
    if not (GRID_X <= x < GRID_X + CELL_W * 4):
        return None

    if not (GRID_Y <= y < GRID_Y + CELL_H * 4):
        return None

    column = (x - GRID_X) // CELL_W
    row = (y - GRID_Y) // CELL_H

    return BUTTONS[row][column]


def run(display, touch, ui):
    """Run the calculator and return EXIT after a right swipe."""

    current = "0"
    stored = None
    operator = None
    replace_current = False
    status = "Swipe right to exit"

    draw_screen(display, ui, current, status)

    while True:
        gesture = touch.capture_gesture()

        if gesture is None:
            time.sleep_ms(10)
            continue

        kind, x, y = gesture

        if kind == "RIGHT":
            return "EXIT"

        if kind != "TAP":
            continue

        label = button_at(x, y)

        if label is None:
            if x < 55 and y < 38:
                return "EXIT"
            continue

        if label.isdigit():
            if current == "0" or replace_current:
                current = label
                replace_current = False
            elif len(current) < 18:
                current += label

        elif label == "C":
            current = "0"
            stored = None
            operator = None
            replace_current = False
            status = "Cleared"

        elif label in ("+", "-", "*", "/"):
            try:
                if stored is not None and operator is not None:
                    stored = calculate(stored, operator, current)
                    current = safe_number_text(stored)
                else:
                    stored = current

                operator = label
                replace_current = True
                status = "Operator " + label

            except Exception:
                current = "ERROR"
                stored = None
                operator = None
                replace_current = True
                status = "Calculation error"

        elif label == "=":
            if stored is not None and operator is not None:
                try:
                    result = calculate(stored, operator, current)
                    current = safe_number_text(result)
                    stored = None
                    operator = None
                    replace_current = True
                    status = "Result"

                except Exception as error:
                    current = "ERROR"
                    stored = None
                    operator = None
                    replace_current = True
                    status = str(error)

        draw_screen(display, ui, current, status)
