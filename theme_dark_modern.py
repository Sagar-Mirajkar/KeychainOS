"""KeychainOS theme: Dark Modern."""

NAME = "dark_modern"
DISPLAY_NAME = "Dark Modern"

# General screen colours
BACKGROUND = 0x0861
STATUS_BACKGROUND = 0x0861
STATUS_TEXT = 0xFFFF
TITLE_TEXT = 0x07FF
PRIMARY_TEXT = 0xFFFF
SECONDARY_TEXT = 0x7DFF
LABEL_TEXT = 0xFFFF
INSTRUCTION_TEXT = 0x07FF

# Carousel tiles
TILE_TOP = 0x10A4
TILE_BOTTOM = 0x0842
TILE_BORDER = 0x07FF
TILE_SHADOW = 0x0000
TILE_GLOSS = 0x7DFF
PEEK_TILE = 0x18E4

# Indicators
DOT_ACTIVE = 0x07FF
DOT_INACTIVE = 0x632C

# Status icons
BATTERY_BORDER = 0xFFFF
BATTERY_FILL = 0x07FF

# Application accents
FILES_TOP = 0xFFE0
FILES_BOTTOM = 0xFD20
GAMES_TOP = 0x04FF
GAMES_BOTTOM = 0x001F
NOTES_TOP = 0xB65F
NOTES_BOTTOM = 0x801F
SETTINGS_TOP = 0xC618
SETTINGS_BOTTOM = 0x4208
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
