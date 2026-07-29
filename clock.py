"""Clock tool for KeychainOS.

Features:
- Live RTC time
- Date display
- 12-hour and 24-hour display modes
- Tap the time to switch format
- Swipe right to exit

The ESP32 RTC must be set separately when accurate real-world time is needed.
"""

from machine import RTC
import time

NAME = "CLOCK"

BLACK = 0x0000
WHITE = 0xFFFF
CYAN = 0x07FF
YELLOW = 0xFFE0
BLUE = 0x001F
DARK = 0x0841
PANEL = 0x18E3
MUTED = 0xA514

rtc = RTC()


def two_digits(value):
    return "{:02d}".format(value)


def month_name(month):
    names = (
        "JAN", "FEB", "MAR", "APR",
        "MAY", "JUN", "JUL", "AUG",
        "SEP", "OCT", "NOV", "DEC"
    )

    if 1 <= month <= 12:
        return names[month - 1]

    return "---"


def weekday_name(weekday):
    names = (
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY"
    )

    if 0 <= weekday <= 6:
        return names[weekday]

    return "UNKNOWN"


def format_time(hour, minute, second, use_24_hour):
    if use_24_hour:
        return (
            two_digits(hour)
            + ":"
            + two_digits(minute)
            + ":"
            + two_digits(second)
        )

    suffix = "AM"
    display_hour = hour

    if hour >= 12:
        suffix = "PM"

    if display_hour == 0:
        display_hour = 12
    elif display_hour > 12:
        display_hour -= 12

    return (
        two_digits(display_hour)
        + ":"
        + two_digits(minute)
        + ":"
        + two_digits(second)
        + " "
        + suffix
    )


def format_date(year, month, day):
    return (
        two_digits(day)
        + " "
        + month_name(month)
        + " "
        + str(year)
    )


def draw_static_screen(display, ui):
    display.fill(DARK)

    display.fill_rect(0, 0, 240, 34, BLUE)
    ui.draw_text(
        display,
        "< CLOCK",
        8,
        8,
        WHITE,
        BLUE,
        72
    )

    display.fill_rect(12, 54, 216, 92, BLACK)
    display.outline_rect(12, 54, 216, 92, CYAN, 2)

    display.fill_rect(22, 166, 196, 54, PANEL)
    display.outline_rect(22, 166, 196, 54, WHITE, 1)

    ui.centred_text(
        display,
        "Tap time: 12 / 24 hour",
        252,
        MUTED,
        DARK
    )

    ui.centred_text(
        display,
        "Swipe right to exit",
        286,
        YELLOW,
        DARK
    )


def draw_dynamic_screen(display, ui, use_24_hour):
    date_time = rtc.datetime()

    year = date_time[0]
    month = date_time[1]
    day = date_time[2]
    weekday = date_time[3]
    hour = date_time[4]
    minute = date_time[5]
    second = date_time[6]

    clock_text = format_time(
        hour,
        minute,
        second,
        use_24_hour
    )

    date_text = format_date(
        year,
        month,
        day
    )

    day_text = weekday_name(weekday)

    display.fill_rect(16, 58, 208, 84, BLACK)
    ui.centred_text(
        display,
        clock_text,
        86,
        CYAN,
        BLACK
    )

    display.fill_rect(26, 170, 188, 46, PANEL)
    ui.centred_text(
        display,
        day_text,
        174,
        WHITE,
        PANEL
    )

    ui.centred_text(
        display,
        date_text,
        195,
        YELLOW,
        PANEL
    )


def run(display, touch, ui):
    """Run the Clock tool and return EXIT after a right swipe."""

    use_24_hour = True
    previous_second = -1

    draw_static_screen(display, ui)
    draw_dynamic_screen(display, ui, use_24_hour)

    while True:
        point = touch.read()

        if point is not None:
            gesture = touch.capture_gesture()

            if gesture is not None:
                kind, x, y = gesture

                if kind == "RIGHT":
                    return "EXIT"

                if kind == "TAP":
                    if x < 55 and y < 42:
                        return "EXIT"

                    if 45 <= y <= 155:
                        use_24_hour = not use_24_hour
                        previous_second = -1

        current_second = rtc.datetime()[6]

        if current_second != previous_second:
            previous_second = current_second
            draw_dynamic_screen(
                display,
                ui,
                use_24_hour
            )

        time.sleep_ms(40)
