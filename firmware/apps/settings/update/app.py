"""KeychainOS Update settings application."""

import machine

from system import updater
from system.ui import (
    PAPER,
    INK,
    MUTED,
    draw_header,
    draw_footer,
    is_back_tap,
)


def draw_message(display, title, line1, line2=""):
    display.fill(PAPER)
    draw_header(display, title, True)
    display.centred_text(line1[:28], 118, INK, PAPER)

    if line2:
        display.centred_text(line2[:28], 150, MUTED, PAPER)

    draw_footer(display, "Tap centre | Swipe right: Back")


def wait_for_action(context):
    while True:
        gesture = context.touch.capture_gesture()

        if gesture is None:
            continue

        kind = gesture["type"]
        x = gesture.get("x", 0)
        y = gesture.get("y", 0)

        if kind == "RIGHT":
            return "BACK"

        if kind == "TAP" and is_back_tap(x, y):
            return "BACK"

        if kind == "TAP":
            return "CONTINUE"


def run(context):
    display = context.display

    draw_message(
        display,
        "Update",
        "Check GitHub for updates",
        "Only changed files install",
    )

    if wait_for_action(context) == "BACK":
        return "BACK"

    def progress(index, total, path, state):
        display.fill(PAPER)
        draw_header(display, "Updating", False)
        display.centred_text(
            "{} of {}".format(index, total),
            92,
            INK,
            PAPER,
        )
        display.centred_text(
            path.rsplit("/", 1)[-1][:28],
            126,
            MUTED,
            PAPER,
        )
        display.centred_text(
            state.upper()[:28],
            158,
            MUTED,
            PAPER,
        )
        draw_footer(display, "Please keep power connected")

    try:
        result = updater.install(progress)

        if result["up_to_date"]:
            draw_message(
                display,
                "Up to date",
                "KeychainOS is current",
                "Version " + str(result["version"]),
            )
            wait_for_action(context)
            return "BACK"

        display.fill(PAPER)
        draw_header(display, "Updated", False)
        display.centred_text(
            "{} file(s) installed".format(result["updated"]),
            112,
            INK,
            PAPER,
        )
        display.centred_text(
            "Version " + str(result["version"]),
            146,
            MUTED,
            PAPER,
        )
        display.centred_text(
            "Tap to restart",
            180,
            MUTED,
            PAPER,
        )
        context.touch.capture_gesture()
        machine.reset()

    except Exception as error:
        display.fill(PAPER)
        draw_header(display, "Update failed", True)
        display.centred_text(
            type(error).__name__[:28],
            108,
            INK,
            PAPER,
        )
        display.centred_text(
            str(error)[:28],
            140,
            MUTED,
            PAPER,
        )
        draw_footer(display, "Tap or swipe right: Back")
        context.touch.capture_gesture()
        return "BACK"
