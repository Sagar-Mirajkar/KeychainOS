"""KeychainOS theme: Minimal Light."""

NAME = "minimal_light"
DISPLAY_NAME = "Minimal Light"

# General screen colours
BACKGROUND = 0xE71C
STATUS_BACKGROUND = 0xE71C
STATUS_TEXT = 0x0000
TITLE_TEXT = 0x0000
PRIMARY_TEXT = 0x0000
SECONDARY_TEXT = 0x4208
LABEL_TEXT = 0x0000
INSTRUCTION_TEXT = 0x4208

# Carousel tiles
TILE_TOP = 0xFFFF
TILE_BOTTOM = 0xDEFB
TILE_BORDER = 0xFFFF
TILE_SHADOW = 0xBDF7
TILE_GLOSS = 0xFFFF
PEEK_TILE = 0xF7BE

# Indicators
DOT_ACTIVE = 0x0000
DOT_INACTIVE = 0xC618

# Status icons
BATTERY_BORDER = 0x0000
BATTERY_FILL = 0x0000

# Application accents
FILES_TOP = 0xFFE0
FILES_BOTTOM = 0xFD20
GAMES_TOP = 0xF81F
GAMES_BOTTOM = 0x8010
NOTES_TOP = 0x07FF
NOTES_BOTTOM = 0x021F
SETTINGS_TOP = 0x5D7F
SETTINGS_BOTTOM = 0x001F
SNAKE_TOP = 0x07E0
SNAKE_BOTTOM = 0x0320
TICTACTOE_TOP = 0x07FF
TICTACTOE_BOTTOM = 0x001F

# Layout values
TILE_SIZE = 132
TILE_X = 54
TILE_Y = 78
PEEK_WIDTH = 22
LABEL_Y = 228
DOT_Y = 268
INSTRUCTION_Y = 288
ACTION_Y = 304

# Style switches used by the future theme-aware UI
SHOW_GLOSS = True
SHOW_SHADOW = True
PIXEL_STYLE = False
COMPACT_LAYOUT = False
ROUNDED_STEPS = 8


def app_colours(name):
    """Return the top and bottom RGB565 colours for an app tile."""

    if name == "FILES":
        return FILES_TOP, FILES_BOTTOM

    if name == "GAMES":
        return GAMES_TOP, GAMES_BOTTOM

    if name == "NOTES":
        return NOTES_TOP, NOTES_BOTTOM

    if name == "SETTINGS":
        return SETTINGS_TOP, SETTINGS_BOTTOM

    if name == "SNAKE":
        return SNAKE_TOP, SNAKE_BOTTOM

    if name == "TIC TAC TOE":
        return TICTACTOE_TOP, TICTACTOE_BOTTOM

    return TILE_TOP, TILE_BOTTOM
