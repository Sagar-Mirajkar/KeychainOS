"""On-device viewer for KeychainOS activity and event logs."""

import activity_log

NAME = "ACTIVITY LOG"

BLACK = 0x0000
WHITE = 0xFFFF
BLUE = 0x001F
CYAN = 0x07FF
YELLOW = 0xFFE0
RED = 0xF800
DARK = 0x0841
MUTED = 0xA514


def _summary(event):
    status = str(event.get("status", ""))
    name = str(event.get("event", "EVENT"))
    return (status + " " + name)[:27]


def run(display, touch, ui):
    offset = 0

    while True:
        events = activity_log.read(200)
        events.reverse()

        display.fill(DARK)
        display.fill_rect(0, 0, 240, 36, BLUE)
        ui.draw_text(display, "< BACK", 8, 9, WHITE, BLUE, 56)
        ui.draw_text(display, "ACTIVITY LOG", 78, 9, WHITE, BLUE, 112)

        visible = events[offset:offset + 11]

        if not visible:
            ui.centred_text(display, "No events recorded", 130, MUTED, DARK)

        for index, event in enumerate(visible):
            y = 44 + index * 24
            colour = RED if event.get("status") == "FAILED" else CYAN
            ui.draw_text(display, _summary(event), 6, y, colour, DARK, 228)

        ui.centred_text(display, "Swipe up/down to scroll", 292, YELLOW, DARK)

        gesture = touch.capture_gesture()

        if gesture is None:
            continue

        kind, x, y = gesture

        if kind == "RIGHT" or (kind == "TAP" and x < 70 and y < 42):
            return "EXIT"

        if kind == "UP":
            offset = min(max(0, len(events) - 11), offset + 5)

        elif kind == "DOWN":
            offset = max(0, offset - 5)
