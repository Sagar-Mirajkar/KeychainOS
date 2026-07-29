"""Theme-aware KeychainOS carousel UI."""

import framebuf
import theme_manager

BLACK = 0x0000
WHITE = 0xFFFF
GREEN = 0x07E0
CYAN = 0x07FF
YELLOW = 0xFFE0
ORANGE = 0xFD20
GAME_PURPLE = 0x8010

WIDTH = 240
HEIGHT = 320

_theme = theme_manager.load_theme()


def get_theme():
    return _theme


def get_theme_name():
    return _theme.NAME


def get_theme_display_name():
    return _theme.DISPLAY_NAME


def set_theme(theme_name, save=True):
    global _theme

    _theme = theme_manager.load_theme(theme_name)

    if save:
        theme_manager.save_theme(theme_name)

    return _theme


def next_theme(save=True):
    theme_name = theme_manager.next_theme(_theme.NAME)
    return set_theme(theme_name, save)


def previous_theme(save=True):
    theme_name = theme_manager.previous_theme(_theme.NAME)
    return set_theme(theme_name, save)


def swap_byte_pairs(data):
    for index in range(0, len(data), 2):
        data[index], data[index + 1] = data[index + 1], data[index]


def draw_text(display, text, x, y, colour=WHITE, background=BLACK,
              width=None, height=16):
    text = str(text)

    if width is None:
        width = WIDTH - x

    if x < 0:
        x = 0

    if y < 0:
        y = 0

    if x >= WIDTH or y >= HEIGHT:
        return

    width = min(width, WIDTH - x)
    height = min(height, HEIGHT - y)

    if width <= 0 or height <= 0:
        return

    text_buffer = bytearray(width * height * 2)
    line = framebuf.FrameBuffer(text_buffer, width, height, framebuf.RGB565)
    line.fill(background)
    line.text(text, 0, 4, colour)
    swap_byte_pairs(text_buffer)

    display.set_window(x, y, x + width - 1, y + height - 1)
    display.sd_cs.value(1)
    display.cs.value(0)
    display.dc.value(1)

    for start in range(0, len(text_buffer), 2048):
        display.spi.write(text_buffer[start:start + 2048])

    display.cs.value(1)


def centred_text(display, text, y, colour=WHITE, background=BLACK):
    text = str(text)
    maximum = WIDTH // 8

    if len(text) > maximum:
        text = text[:maximum]

    text_width = len(text) * 8
    x = (WIDTH - text_width) // 2
    draw_text(display, text, x, y, colour, background, text_width)


def draw_status_bar(display, section):
    theme = _theme
    display.fill_rect(0, 0, WIDTH, 27, theme.STATUS_BACKGROUND)
    draw_text(display, "9:41", 8, 4, theme.STATUS_TEXT,
              theme.STATUS_BACKGROUND, 40)
    draw_text(display, section[:10], 82, 4, theme.STATUS_TEXT,
              theme.STATUS_BACKGROUND, 80)
    display.outline_rect(202, 8, 27, 11, theme.BATTERY_BORDER, 1)
    display.fill_rect(229, 11, 3, 5, theme.BATTERY_BORDER)
    display.fill_rect(205, 11, 18, 5, theme.BATTERY_FILL)


def draw_soft_tile(display, x, y, size, top_colour, bottom_colour):
    theme = _theme

    if theme.PIXEL_STYLE:
        display.fill_rect(x, y, size, size, bottom_colour)
        display.outline_rect(x, y, size, size, theme.TILE_BORDER, 4)
        return

    if theme.SHOW_SHADOW:
        display.fill_rect(x + 4, y + 5, size, size, theme.TILE_SHADOW)

    step = theme.ROUNDED_STEPS

    if step < 1:
        display.fill_rect(x, y, size, size, top_colour)
    else:
        display.fill_rect(x + step, y, size - step * 2, 3, top_colour)
        display.fill_rect(x + 4, y + 3, size - 8, 4, top_colour)
        display.fill_rect(x, y + 7, size, size - 14, top_colour)
        display.fill_rect(x + 1, y + size // 2, size - 2,
                          size // 2 - 7, bottom_colour)
        display.fill_rect(x + 4, y + size - 7, size - 8, 4, bottom_colour)
        display.fill_rect(x + step, y + size - 3,
                          size - step * 2, 3, bottom_colour)

    if theme.SHOW_GLOSS:
        display.fill_rect(x + 8, y + 9, size - 16, 4, theme.TILE_GLOSS)
        display.fill_rect(x + 12, y + 13, size - 24, 2, WHITE)

    display.outline_rect(x + 4, y + 3, size - 8, size - 6,
                         theme.TILE_BORDER, 1)


def draw_folder_icon(display, x, y):
    display.fill_rect(x + 5, y + 15, 58, 38, YELLOW)
    display.fill_rect(x + 11, y + 7, 25, 12, YELLOW)
    display.fill_rect(x + 9, y + 24, 50, 3, ORANGE)


def draw_gamepad_icon(display, x, y):
    display.fill_rect(x + 5, y + 17, 60, 34, GAME_PURPLE)
    display.fill_rect(x + 13, y + 10, 44, 48, GAME_PURPLE)
    display.fill_rect(x + 17, y + 28, 18, 6, WHITE)
    display.fill_rect(x + 23, y + 22, 6, 18, WHITE)
    display.fill_rect(x + 48, y + 25, 7, 7, CYAN)
    display.fill_rect(x + 56, y + 34, 7, 7, YELLOW)


def draw_snake_icon(display, x, y):
    blocks = ((0, 24), (10, 24), (20, 24), (20, 14),
              (30, 14), (40, 14), (40, 24), (50, 24))

    for block_x, block_y in blocks:
        display.fill_rect(x + block_x, y + block_y, 9, 9, GREEN)

    display.fill_rect(x + 57, y + 27, 3, 3, BLACK)
    display.fill_rect(x + 66, y + 16, 8, 8, 0xF800)


def draw_tic_tac_toe_icon(display, x, y):
    display.fill_rect(x + 22, y + 5, 3, 58, WHITE)
    display.fill_rect(x + 45, y + 5, 3, 58, WHITE)
    display.fill_rect(x + 4, y + 23, 62, 3, WHITE)
    display.fill_rect(x + 4, y + 45, 62, 3, WHITE)

    for offset in range(0, 13, 3):
        display.fill_rect(x + 7 + offset, y + 8 + offset, 3, 3, 0xF960)
        display.fill_rect(x + 19 - offset, y + 8 + offset, 3, 3, 0xF960)

    display.outline_rect(x + 28, y + 29, 14, 14, 0x04FF, 3)


def draw_notes_icon(display, x, y):
    display.fill_rect(x + 10, y + 7, 50, 51, WHITE)

    for offset, line_width in ((17, 36), (27, 36), (37, 28), (47, 32)):
        display.fill_rect(x + 17, y + offset, line_width, 3, 0x021F)


def draw_settings_icon(display, x, y, background):
    display.fill_rect(x + 25, y + 10, 20, 48, CYAN)
    display.fill_rect(x + 11, y + 24, 48, 20, CYAN)
    display.fill_rect(x + 18, y + 17, 34, 34, CYAN)
    display.fill_rect(x + 27, y + 26, 16, 16, background)


def draw_app_icon(display, name, x, y, size, background):
    icon_x = x + (size - 72) // 2
    icon_y = y + max(18, (size - 80) // 3)

    if name == "FILES":
        draw_folder_icon(display, icon_x, icon_y)
    elif name == "GAMES":
        draw_gamepad_icon(display, icon_x, icon_y)
    elif name == "NOTES":
        draw_notes_icon(display, icon_x, icon_y)
    elif name == "SETTINGS":
        draw_settings_icon(display, icon_x, icon_y, background)
    elif name == "SNAKE":
        draw_snake_icon(display, icon_x, icon_y)
    elif name == "TIC TAC TOE":
        draw_tic_tac_toe_icon(display, icon_x, icon_y)


def draw_carousel(display, items, selected, section):
    theme = _theme
    tile_size = theme.TILE_SIZE
    tile_x = theme.TILE_X
    tile_y = theme.TILE_Y

    display.fill(theme.BACKGROUND)
    draw_status_bar(display, section)

    previous_name = items[(selected - 1) % len(items)]
    current_name = items[selected]
    next_name = items[(selected + 1) % len(items)]

    previous_colours = theme.app_colours(previous_name)
    current_colours = theme.app_colours(current_name)
    next_colours = theme.app_colours(next_name)

    peek_y = tile_y + 18
    left_x = -tile_size + theme.PEEK_WIDTH
    right_x = WIDTH - theme.PEEK_WIDTH

    display.fill_rect(left_x, peek_y, tile_size, tile_size - 36,
                      previous_colours[1])
    display.fill_rect(right_x, peek_y, tile_size, tile_size - 36,
                      next_colours[1])

    draw_soft_tile(display, tile_x, tile_y, tile_size,
                   current_colours[0], current_colours[1])
    draw_app_icon(display, current_name, tile_x, tile_y,
                  tile_size, current_colours[1])

    centred_text(display, current_name, theme.LABEL_Y,
                 theme.LABEL_TEXT, theme.BACKGROUND)

    dot_start = (WIDTH - len(items) * 18) // 2

    for index in range(len(items)):
        dot_colour = theme.DOT_ACTIVE if index == selected else theme.DOT_INACTIVE
        display.fill_rect(dot_start + index * 18, theme.DOT_Y,
                          10, 6, dot_colour)

    centred_text(display, "Swipe to browse", theme.INSTRUCTION_Y,
                 theme.INSTRUCTION_TEXT, theme.BACKGROUND)
    centred_text(display, "Tap to open", theme.ACTION_Y,
                 theme.PRIMARY_TEXT, theme.BACKGROUND)


def draw_placeholder(display, title, message):
    theme = _theme
    display.fill(theme.BACKGROUND)
    draw_status_bar(display, title)

    colours = theme.app_colours(title)
    draw_soft_tile(display, theme.TILE_X, 70, theme.TILE_SIZE,
                   colours[0], colours[1])
    draw_app_icon(display, title, theme.TILE_X, 70,
                  theme.TILE_SIZE, colours[1])
    centred_text(display, title, 222, theme.LABEL_TEXT, theme.BACKGROUND)
    centred_text(display, message, 260, theme.TITLE_TEXT, theme.BACKGROUND)
    centred_text(display, "Swipe right to return", 292,
                 theme.SECONDARY_TEXT, theme.BACKGROUND)


def draw_theme_settings(display, selected_index):
    theme = _theme
    names = theme_manager.THEMES
    selected_name = names[selected_index]
    preview = theme_manager.load_theme(selected_name)

    display.fill(preview.BACKGROUND)
    draw_status_bar(display, "Themes")

    centred_text(display, "THEME", 44,
                 preview.TITLE_TEXT, preview.BACKGROUND)
    centred_text(display, preview.DISPLAY_NAME, 70,
                 preview.TITLE_TEXT, preview.BACKGROUND)

    colours = preview.app_colours("SETTINGS")
    draw_soft_tile(display, preview.TILE_X, 102,
                   preview.TILE_SIZE, colours[0], colours[1])
    draw_settings_icon(display,
                       preview.TILE_X + (preview.TILE_SIZE - 72) // 2,
                       126,
                       colours[1])

    dot_start = (WIDTH - len(names) * 18) // 2

    for index in range(len(names)):
        dot_colour = preview.DOT_ACTIVE if index == selected_index else preview.DOT_INACTIVE
        display.fill_rect(dot_start + index * 18, 254, 10, 6, dot_colour)

    centred_text(display, "Swipe to preview", 278,
                 preview.INSTRUCTION_TEXT, preview.BACKGROUND)
    centred_text(display, "Tap to apply", 298,
                 preview.PRIMARY_TEXT, preview.BACKGROUND)
