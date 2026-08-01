"""KeychainOS dynamic full-colour e-paper-style UI."""

from system.display import (
    WIDTH,
    HEIGHT,
    BLACK,
    WHITE,
    RED,
    GREEN,
    BLUE,
    CYAN,
    YELLOW,
)

# Full-colour e-paper-inspired palette.
PAPER = 0xFF9C
INK = 0x18E3
MUTED = 0x738E
BORDER = 0xAD55
CARD = 0xF7BB
CARD_SELECTED = WHITE
TEAL = 0x04D3
TEAL_DARK = 0x02A9
SOFT_RED = 0xE186
SOFT_BLUE = 0x9D7F
SOFT_GREEN = 0xA6CE
SOFT_YELLOW = 0xED47
SOFT_PURPLE = 0xC4D8

HEADER_HEIGHT = 42
FOOTER_HEIGHT = 24
GRID_TOP = 48
GRID_LEFT = 6
GRID_COLUMNS = 3
GRID_ROWS = 3
CARD_WIDTH = 72
CARD_HEIGHT = 76
CARD_GAP_X = 6
CARD_GAP_Y = 7
ITEMS_PER_PAGE = GRID_COLUMNS * GRID_ROWS
BACK_RECT = (4, 4, 62, 32)


def trim_text(text, limit):
    text = str(text)
    if len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3] + "..."


def draw_text(display, text, x, y, colour=INK, background=PAPER, width=None, height=16):
    display.draw_text(text, x, y, colour, background, width, height)


def centred_text(display, text, y, colour=INK, background=PAPER):
    display.centred_text(text, y, colour, background)


def draw_back_button(display):
    x, y, width, height = BACK_RECT
    display.fill_rect(x, y, width, height, CARD)
    display.outline_rect(x, y, width, height, BORDER, 1)
    display.draw_text("< BACK", x + 7, y + 8, INK, CARD, 48)


def is_back_tap(x, y):
    bx, by, width, height = BACK_RECT
    return bx <= x < bx + width and by <= y < by + height


def draw_header(display, title, show_back=False):
    display.fill_rect(0, 0, WIDTH, HEADER_HEIGHT, PAPER)
    display.fill_rect(0, HEADER_HEIGHT - 1, WIDTH, 1, BORDER)
    if show_back:
        draw_back_button(display)
        title_x = 72
        title_width = WIDTH - 78
    else:
        title_x = 8
        title_width = WIDTH - 16
    display.draw_text(trim_text(title, title_width // 8), title_x, 12, INK, PAPER, title_width)


def draw_footer(display, text="Tap to open | Hold for menu"):
    y = HEIGHT - FOOTER_HEIGHT
    display.fill_rect(0, y, WIDTH, FOOTER_HEIGHT, PAPER)
    display.fill_rect(0, y, WIDTH, 1, BORDER)
    label = trim_text(text, 29)
    display.centred_text(label, y + 5, MUTED, PAPER)


def icon_colour(name):
    value = sum(ord(character) for character in str(name)) % 6
    return (
        SOFT_BLUE,
        SOFT_GREEN,
        SOFT_YELLOW,
        SOFT_PURPLE,
        SOFT_RED,
        TEAL,
    )[value]


def draw_generic_icon(display, name, x, y, selected=False):
    colour = icon_colour(name)
    display.fill_rect(x, y, 34, 30, colour)
    display.outline_rect(x, y, 34, 30, INK if selected else BORDER, 1)
    letter = str(name).strip()[:1].upper() or "?"
    display.draw_text(letter, x + 13, y + 7, INK, colour, 8)


def item_rect(index_on_page):
    column = index_on_page % GRID_COLUMNS
    row = index_on_page // GRID_COLUMNS
    x = GRID_LEFT + column * (CARD_WIDTH + CARD_GAP_X)
    y = GRID_TOP + row * (CARD_HEIGHT + CARD_GAP_Y)
    return x, y, CARD_WIDTH, CARD_HEIGHT


def draw_card(display, item, page_index, selected=False):
    x, y, width, height = item_rect(page_index)
    background = CARD_SELECTED if selected else CARD
    border = TEAL_DARK if selected else BORDER
    if selected:
        display.fill_rect(x + 3, y + 3, width, height, 0xCE59)
    display.fill_rect(x, y, width, height, background)
    display.outline_rect(x, y, width, height, border, 2 if selected else 1)
    name = item.get("name", "Unnamed") if isinstance(item, dict) else str(item)
    draw_generic_icon(display, name, x + 19, y + 9, selected)
    label = trim_text(name.upper(), 8)
    label_width = max(8, len(label) * 8)
    display.draw_text(label, x + (width - label_width) // 2, y + 49, INK, background, label_width)
    if isinstance(item, dict):
        if item.get("broken"):
            display.fill_rect(x + width - 12, y + 4, 8, 8, SOFT_RED)
        elif item.get("update"):
            display.fill_rect(x + width - 12, y + 4, 8, 8, SOFT_YELLOW)


def normalize_items(items):
    result = []
    for item in items or ():
        if isinstance(item, dict):
            result.append(item)
        else:
            result.append({"name": str(item)})
    return result


def draw_grid(display, items, selected=0, title="KeychainOS", show_back=False):
    items = normalize_items(items)
    count = len(items)
    if count:
        selected %= count
        page = selected // ITEMS_PER_PAGE
    else:
        selected = 0
        page = 0

    display.fill(PAPER)
    draw_header(display, title, show_back)

    if not items:
        display.centred_text("No items installed", 132, MUTED, PAPER)
        display.centred_text("Swipe down to refresh", 158, MUTED, PAPER)
        draw_footer(display, "Hold empty area for options")
        return {"page": 0, "pages": 1, "selected": 0}

    start = page * ITEMS_PER_PAGE
    visible = items[start : start + ITEMS_PER_PAGE]
    for local_index, item in enumerate(visible):
        draw_card(display, item, local_index, start + local_index == selected)

    pages = (count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    if pages > 1:
        dot_width = 8
        gap = 6
        total = pages * dot_width + (pages - 1) * gap
        dot_x = (WIDTH - total) // 2
        dot_y = HEIGHT - FOOTER_HEIGHT - 9
        for page_index in range(pages):
            colour = TEAL_DARK if page_index == page else BORDER
            display.fill_rect(dot_x + page_index * (dot_width + gap), dot_y, dot_width, 4, colour)

    draw_footer(display)
    return {"page": page, "pages": pages, "selected": selected}


def draw_carousel(display, items, selected, section="KeychainOS"):
    """Compatibility wrapper using the dynamic grid renderer."""
    show_back = section not in ("KeychainOS", "Home")
    return draw_grid(display, items, selected, section, show_back)


def item_at(x, y, items, selected=0):
    items = normalize_items(items)
    if not items or y < GRID_TOP:
        return None
    page = (selected % len(items)) // ITEMS_PER_PAGE
    start = page * ITEMS_PER_PAGE
    for local_index in range(min(ITEMS_PER_PAGE, len(items) - start)):
        rx, ry, width, height = item_rect(local_index)
        if rx <= x < rx + width and ry <= y < ry + height:
            return start + local_index
    return None


def draw_dialog(display, title, message, buttons=("OK",), danger=False):
    display.fill_rect(16, 74, 208, 172, WHITE)
    display.outline_rect(16, 74, 208, 172, SOFT_RED if danger else TEAL_DARK, 2)
    display.centred_text(trim_text(title, 25), 88, SOFT_RED if danger else INK, WHITE)
    lines = []
    message = str(message)
    while message:
        lines.append(message[:25])
        message = message[25:]
    for index, line in enumerate(lines[:4]):
        display.centred_text(line, 118 + index * 20, INK, WHITE)
    button_count = max(1, len(buttons))
    gap = 6
    button_width = (188 - gap * (button_count - 1)) // button_count
    for index, label in enumerate(buttons):
        x = 26 + index * (button_width + gap)
        display.fill_rect(x, 204, button_width, 32, CARD)
        display.outline_rect(x, 204, button_width, 32, SOFT_RED if danger else BORDER, 1)
        label = trim_text(label, max(1, (button_width - 4) // 8))
        display.draw_text(label, x + 4, 212, INK, CARD, button_width - 8)
    return (26, 204, button_width, 32, gap)


def dialog_choice(x, y, buttons, geometry):
    start_x, start_y, width, height, gap = geometry
    if not (start_y <= y < start_y + height):
        return None
    for index, label in enumerate(buttons):
        bx = start_x + index * (width + gap)
        if bx <= x < bx + width:
            return label
    return None


def draw_placeholder(display, title, message):
    display.fill(PAPER)
    draw_header(display, title, True)
    display.centred_text(trim_text(message, 28), 138, MUTED, PAPER)
    draw_footer(display, "Tap Back to return")


def draw_error(display, title, error):
    display.fill(PAPER)
    draw_header(display, "Error", True)
    display.centred_text(trim_text(title, 28), 96, SOFT_RED, PAPER)
    display.centred_text(trim_text(type(error).__name__, 28), 126, INK, PAPER)
    display.centred_text(trim_text(str(error), 28), 154, MUTED, PAPER)
    draw_footer(display, "Tap Back to continue")
