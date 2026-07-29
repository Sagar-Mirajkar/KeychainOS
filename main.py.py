from machine import Pin, SPI, I2C
import framebuf
import random
import time
import gc

# =========================================================
# KEYCHAINOS STAGE 2
# Swipeable thumbnail home menu + Games menu + Snake
# No SD-card dependency
# =========================================================

# Waveshare ESP32-S3 LCD Driver Board: LCD
LCD_SCLK = 1
LCD_MOSI = 2
LCD_MISO = 42
LCD_CS = 39
LCD_DC = 41
LCD_RST = 40
LCD_BL = 6
SD_CS = 38

# CST816D touch
TP_SDA = 15
TP_SCL = 7
TP_RST = 16
TP_INT = 17
TP_ADDRESS = 0x15

WIDTH = 240
HEIGHT = 320

# Keep the orientation values that worked in the colour-swipe test.
TOUCH_SWAP_XY = False
TOUCH_INVERT_X = False
TOUCH_INVERT_Y = False
SWIPE_THRESHOLD = 35

# RGB565 colours
BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
CYAN = 0x07FF
YELLOW = 0xFFE0
MAGENTA = 0xF81F
ORANGE = 0xFD20
DARK_BG = 0x0841
HEADER = 0x021F
CARD = 0x18E3
CARD_ALT = 0x2104
BORDER = 0x528A
MUTED = 0xA514
FOLDER_YELLOW = 0xFFE0
GAME_PURPLE = 0x8010
SNAKE_GREEN = 0x07E0
FOOD_RED = 0xF800
TICTAC_BLUE = 0x04FF
TICTAC_RED = 0xF960
WIN_GREEN = 0x07E0

# iPod nano-inspired horizontal carousel layout
# One large centred tile is active; neighbouring tiles peek in from the sides.
CAROUSEL_TILE = 132
CAROUSEL_X = 54
CAROUSEL_Y = 78
CAROUSEL_RADIUS_HINT = 10
PEEK_W = 22

# Current UI state
screen_mode = "HOME"
home_index = 0
HOME_APPS = ("FILES", "GAMES", "NOTES", "SETTINGS")
games_index = 0
GAME_APPS = ("SNAKE", "TIC TAC TOE")

# Snake settings
GRID_SIZE = 12
PLAY_X = 0
PLAY_Y = 48
PLAY_W = 240
PLAY_H = 240
COLS = PLAY_W // GRID_SIZE
ROWS = PLAY_H // GRID_SIZE
SNAKE_STEP_MS = 180

# =========================================================
# LCD DRIVER
# =========================================================

lcd_cs = Pin(LCD_CS, Pin.OUT, value=1)
lcd_dc = Pin(LCD_DC, Pin.OUT, value=0)
lcd_rst = Pin(LCD_RST, Pin.OUT, value=1)
lcd_bl = Pin(LCD_BL, Pin.OUT, value=0)
sd_cs = Pin(SD_CS, Pin.OUT, value=1)

spi = SPI(
    2,
    baudrate=20_000_000,
    polarity=0,
    phase=0,
    sck=Pin(LCD_SCLK),
    mosi=Pin(LCD_MOSI),
    miso=Pin(LCD_MISO)
)


def lcd_command(command, data=None):
    sd_cs.value(1)
    lcd_cs.value(0)
    lcd_dc.value(0)
    spi.write(bytes([command]))
    if data is not None:
        lcd_dc.value(1)
        spi.write(data)
    lcd_cs.value(1)


def init_display():
    lcd_bl.value(0)
    sd_cs.value(1)

    lcd_rst.value(1)
    time.sleep_ms(10)
    lcd_rst.value(0)
    time.sleep_ms(100)
    lcd_rst.value(1)
    time.sleep_ms(120)

    lcd_command(0x01)
    time.sleep_ms(150)
    lcd_command(0x11)
    time.sleep_ms(120)
    lcd_command(0x3A, b"\x55")
    lcd_command(0x36, b"\x00")
    lcd_command(0x21)
    lcd_command(0x13)
    lcd_command(0x29)
    time.sleep_ms(100)
    lcd_bl.value(1)


def set_window(x0, y0, x1, y1):
    lcd_command(0x2A, bytes([
        x0 >> 8, x0 & 0xFF,
        x1 >> 8, x1 & 0xFF
    ]))
    lcd_command(0x2B, bytes([
        y0 >> 8, y0 & 0xFF,
        y1 >> 8, y1 & 0xFF
    ]))
    lcd_command(0x2C)


def fill_rect(x, y, width, height, colour):
    if width <= 0 or height <= 0:
        return

    x = max(0, x)
    y = max(0, y)
    width = min(width, WIDTH - x)
    height = min(height, HEIGHT - y)
    if width <= 0 or height <= 0:
        return

    set_window(x, y, x + width - 1, y + height - 1)
    pixel = bytes([(colour >> 8) & 0xFF, colour & 0xFF])
    chunk_pixels = 256
    chunk = pixel * chunk_pixels
    count = width * height

    sd_cs.value(1)
    lcd_cs.value(0)
    lcd_dc.value(1)

    for _ in range(count // chunk_pixels):
        spi.write(chunk)
    remaining = count % chunk_pixels
    if remaining:
        spi.write(pixel * remaining)

    lcd_cs.value(1)


def fill_screen(colour):
    fill_rect(0, 0, WIDTH, HEIGHT, colour)


def outline_rect(x, y, width, height, colour, thickness=2):
    fill_rect(x, y, width, thickness, colour)
    fill_rect(x, y + height - thickness, width, thickness, colour)
    fill_rect(x, y, thickness, height, colour)
    fill_rect(x + width - thickness, y, thickness, height, colour)


def swap_byte_pairs(data):
    for index in range(0, len(data), 2):
        data[index], data[index + 1] = data[index + 1], data[index]


def draw_text(text, x, y, colour=WHITE, background=DARK_BG,
              width=None, height=16):
    if width is None:
        width = WIDTH - x
    width = max(1, min(width, WIDTH - x))

    text_buffer = bytearray(width * height * 2)
    text_line = framebuf.FrameBuffer(
        text_buffer, width, height, framebuf.RGB565
    )
    text_line.fill(background)
    text_line.text(text, 0, 4, colour)
    swap_byte_pairs(text_buffer)

    set_window(x, y, x + width - 1, y + height - 1)
    sd_cs.value(1)
    lcd_cs.value(0)
    lcd_dc.value(1)
    for start in range(0, len(text_buffer), 2048):
        spi.write(text_buffer[start:start + 2048])
    lcd_cs.value(1)

# =========================================================
# TOUCH DRIVER
# =========================================================

touch_rst = Pin(TP_RST, Pin.OUT, value=1)
touch_int = Pin(TP_INT, Pin.IN, Pin.PULL_UP)
touch_i2c = I2C(
    1,
    scl=Pin(TP_SCL),
    sda=Pin(TP_SDA),
    freq=400_000
)


def init_touch():
    touch_rst.value(0)
    time.sleep_ms(200)
    touch_rst.value(1)
    time.sleep_ms(300)
    devices = touch_i2c.scan()
    print("I2C devices:", [hex(device) for device in devices])
    return TP_ADDRESS in devices


def transform_touch(raw_x, raw_y):
    x, y = raw_x, raw_y
    if TOUCH_SWAP_XY:
        x, y = y, x
    if TOUCH_INVERT_X:
        x = WIDTH - 1 - x
    if TOUCH_INVERT_Y:
        y = HEIGHT - 1 - y
    return x, y


def read_touch():
    try:
        count = touch_i2c.readfrom_mem(TP_ADDRESS, 0x02, 1)[0]
        if count == 0:
            return None
        data = touch_i2c.readfrom_mem(TP_ADDRESS, 0x03, 4)
        x = ((data[0] & 0x0F) << 8) | data[1]
        y = ((data[2] & 0x0F) << 8) | data[3]
        return transform_touch(x, y)
    except OSError:
        return None


def capture_gesture():
    start = None
    end = None
    missing = 0

    while True:
        point = read_touch()
        if point is not None:
            missing = 0
            if start is None:
                start = point
            end = point
        elif start is not None:
            missing += 1
            if missing >= 3:
                break
        time.sleep_ms(10)

    if start is None or end is None:
        return None

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    print("Gesture:", start, "to", end, "delta", dx, dy)

    if abs(dx) >= SWIPE_THRESHOLD and abs(dx) > abs(dy):
        return ("LEFT" if dx < 0 else "RIGHT", end[0], end[1])
    if abs(dy) >= SWIPE_THRESHOLD and abs(dy) > abs(dx):
        return ("UP" if dy < 0 else "DOWN", end[0], end[1])
    return ("TAP", end[0], end[1])

# =========================================================
# ICONS AND THUMBNAILS
# =========================================================


def draw_folder_icon(x, y, background):
    fill_rect(x + 5, y + 15, 58, 38, FOLDER_YELLOW)
    fill_rect(x + 11, y + 7, 25, 12, FOLDER_YELLOW)
    fill_rect(x + 9, y + 24, 50, 3, ORANGE)


def draw_gamepad_icon(x, y, background):
    # Simple pixel-style controller icon
    fill_rect(x + 5, y + 17, 60, 34, GAME_PURPLE)
    fill_rect(x + 13, y + 10, 44, 48, GAME_PURPLE)
    # D-pad
    fill_rect(x + 17, y + 28, 18, 6, WHITE)
    fill_rect(x + 23, y + 22, 6, 18, WHITE)
    # Buttons
    fill_rect(x + 48, y + 25, 7, 7, CYAN)
    fill_rect(x + 56, y + 34, 7, 7, YELLOW)


def draw_snake_icon(x, y, background):
    # Segmented snake thumbnail
    blocks = (
        (0, 24), (10, 24), (20, 24),
        (20, 14), (30, 14), (40, 14),
        (40, 24), (50, 24)
    )
    for bx, by in blocks:
        fill_rect(x + bx, y + by, 9, 9, SNAKE_GREEN)
    fill_rect(x + 57, y + 27, 3, 3, BLACK)
    fill_rect(x + 66, y + 16, 8, 8, FOOD_RED)


def draw_tictactoe_icon(x, y, background):
    # 3 x 3 grid
    fill_rect(x + 22, y + 5, 3, 58, WHITE)
    fill_rect(x + 45, y + 5, 3, 58, WHITE)
    fill_rect(x + 4, y + 23, 62, 3, WHITE)
    fill_rect(x + 4, y + 45, 62, 3, WHITE)

    # X in the top-left cell
    for offset in range(0, 13, 3):
        fill_rect(x + 7 + offset, y + 8 + offset, 3, 3, TICTAC_RED)
        fill_rect(x + 19 - offset, y + 8 + offset, 3, 3, TICTAC_RED)

    # O represented by a square ring in the centre cell
    outline_rect(x + 28, y + 29, 14, 14, TICTAC_BLUE, 3)


def draw_notes_icon(x, y, background):
    fill_rect(x + 10, y + 7, 50, 51, WHITE)
    fill_rect(x + 17, y + 17, 36, 3, HEADER)
    fill_rect(x + 17, y + 27, 36, 3, HEADER)
    fill_rect(x + 17, y + 37, 28, 3, HEADER)
    fill_rect(x + 17, y + 47, 32, 3, HEADER)


def draw_settings_icon(x, y, background):
    # Pixel-style settings symbol
    fill_rect(x + 25, y + 10, 20, 48, CYAN)
    fill_rect(x + 11, y + 24, 48, 20, CYAN)
    fill_rect(x + 18, y + 17, 34, 34, CYAN)
    fill_rect(x + 27, y + 26, 16, 16, background)


def draw_soft_tile(x, y, size, top_colour, bottom_colour):
    """Draw a layered glossy square tile without a full-screen framebuffer."""
    # Shadow
    fill_rect(x + 4, y + 5, size, size, BLACK)

    # Rounded-corner illusion with horizontal stepped bands
    fill_rect(x + 8, y, size - 16, 3, top_colour)
    fill_rect(x + 4, y + 3, size - 8, 4, top_colour)
    fill_rect(x, y + 7, size, size - 14, top_colour)
    fill_rect(x + 4, y + size - 7, size - 8, 4, bottom_colour)
    fill_rect(x + 8, y + size - 3, size - 16, 3, bottom_colour)

    # Lower colour area
    fill_rect(x + 1, y + size // 2, size - 2, size // 2 - 7, bottom_colour)

    # Gloss/reflection
    fill_rect(x + 8, y + 9, size - 16, 4, WHITE)
    fill_rect(x + 12, y + 13, size - 24, 2, 0xCFFF)

    outline_rect(x + 4, y + 3, size - 8, size - 6, WHITE, 1)


def draw_app_icon(name, x, y, size, background):
    icon_x = x + (size - 72) // 2
    icon_y = y + 26

    if name == "FILES":
        draw_folder_icon(icon_x, icon_y, background)
    elif name == "GAMES":
        draw_gamepad_icon(icon_x, icon_y, background)
    elif name == "NOTES":
        draw_notes_icon(icon_x, icon_y, background)
    elif name == "SETTINGS":
        draw_settings_icon(icon_x, icon_y, background)
    elif name == "SNAKE":
        draw_snake_icon(icon_x, icon_y, background)
    elif name == "TIC TAC TOE":
        draw_tictactoe_icon(icon_x, icon_y, background)


def app_colours(name):
    if name == "FILES":
        return 0xFFE0, 0xFD20
    if name == "GAMES":
        return 0xF81F, 0x8010
    if name == "NOTES":
        return 0x07FF, 0x021F
    if name == "SETTINGS":
        return 0xC618, 0x4208
    if name == "SNAKE":
        return 0x07E0, 0x0320
    return 0x07FF, 0x001F


def draw_status_bar(section):
    fill_rect(0, 0, WIDTH, 27, 0xBDF7)
    draw_text("9:41", 8, 4, BLACK, 0xBDF7, 40)
    draw_text(section, 82, 4, BLACK, 0xBDF7, 80)

    # Simple battery symbol
    outline_rect(202, 8, 27, 11, BLACK, 1)
    fill_rect(229, 11, 3, 5, BLACK)
    fill_rect(205, 11, 18, 5, GREEN)


def draw_peek_tile(side, colour):
    y = CAROUSEL_Y + 18
    if side == "LEFT":
        x = -CAROUSEL_TILE + PEEK_W
    else:
        x = WIDTH - PEEK_W
    fill_rect(x, y, CAROUSEL_TILE, CAROUSEL_TILE - 36, colour)
    outline_rect(x, y, CAROUSEL_TILE, CAROUSEL_TILE - 36, WHITE, 2)


def draw_carousel(items, selected, section):
    fill_screen(0xBDF7)
    draw_status_bar(section)

    previous_name = items[(selected - 1) % len(items)]
    current_name = items[selected]
    next_name = items[(selected + 1) % len(items)]

    previous_top, previous_bottom = app_colours(previous_name)
    current_top, current_bottom = app_colours(current_name)
    next_top, next_bottom = app_colours(next_name)

    draw_peek_tile("LEFT", previous_bottom)
    draw_peek_tile("RIGHT", next_bottom)

    draw_soft_tile(
        CAROUSEL_X,
        CAROUSEL_Y,
        CAROUSEL_TILE,
        current_top,
        current_bottom
    )
    draw_app_icon(
        current_name,
        CAROUSEL_X,
        CAROUSEL_Y,
        CAROUSEL_TILE,
        current_bottom
    )

    # Label below selected tile
    label_width = min(216, len(current_name) * 8 + 24)
    label_x = (WIDTH - label_width) // 2
    fill_rect(label_x, 224, label_width, 28, 0xBDF7)
    draw_text(
        current_name,
        (WIDTH - len(current_name) * 8) // 2,
        228,
        WHITE,
        0xBDF7,
        len(current_name) * 8
    )

    # Page indicators
    dot_start = (WIDTH - len(items) * 18) // 2
    for index in range(len(items)):
        dot_colour = WHITE if index == selected else 0x7BEF
        fill_rect(dot_start + index * 18, 268, 10, 6, dot_colour)

    draw_text("Swipe to browse", 64, 288, 0x4208, 0xBDF7, 120)
    draw_text("Tap to open", 76, 304, BLACK, 0xBDF7, 96)


def draw_home():
    global screen_mode
    screen_mode = "HOME"
    draw_carousel(HOME_APPS, home_index, "KeychainOS")


def draw_games_menu():
    global screen_mode
    screen_mode = "GAMES"
    draw_carousel(GAME_APPS, games_index, "Games")


def handle_home_tap(x, y):
    selected = HOME_APPS[home_index]

    if selected == "FILES":
        draw_files_placeholder()
    elif selected == "GAMES":
        draw_games_menu()
    elif selected == "NOTES":
        draw_placeholder("NOTES", "Coming in a later stage")
    elif selected == "SETTINGS":
        draw_placeholder("SETTINGS", "Coming in a later stage")


def handle_games_tap(x, y):
    selected = GAME_APPS[games_index]

    if selected == "SNAKE":
        run_snake_game()
    elif selected == "TIC TAC TOE":
        run_tic_tac_toe()


def draw_files_placeholder():
    global screen_mode
    screen_mode = "FILES_PLACEHOLDER"
    fill_screen(0xBDF7)
    draw_status_bar("Files")
    draw_soft_tile(54, 70, 132, 0xFFE0, 0xFD20)
    draw_folder_icon(84, 102, 0xFD20)
    draw_text("FILES", 100, 222, WHITE, 0xBDF7, 40)
    draw_text("SD support postponed", 40, 260, BLACK, 0xBDF7, 168)
    draw_text("Swipe right to return", 36, 292, 0x4208, 0xBDF7, 176)


def draw_placeholder(title, message):
    global screen_mode
    screen_mode = "PLACEHOLDER"
    fill_screen(0xBDF7)
    draw_status_bar(title)
    top, bottom = app_colours(title)
    draw_soft_tile(54, 70, 132, top, bottom)
    draw_app_icon(title, 54, 70, 132, bottom)
    draw_text(title, (WIDTH - len(title) * 8) // 2,
              222, WHITE, 0xBDF7, len(title) * 8)
    draw_text(message, 20, 260, BLACK, 0xBDF7, 200)
    draw_text("Swipe right to return", 36, 292, 0x4208, 0xBDF7, 176)

# =========================================================
# SNAKE GAME
# =========================================================


def random_food(snake):
    while True:
        point = (random.randrange(COLS), random.randrange(ROWS))
        if point not in snake:
            return point


def draw_snake_header(score):
    fill_rect(0, 0, WIDTH, 48, HEADER)
    draw_text("< SNAKE", 8, 5, WHITE, HEADER, 80)
    draw_text("SCORE {}".format(score), 144, 5, YELLOW, HEADER, 88)
    draw_text("Swipe to steer", 64, 27, CYAN, HEADER, 120)


def draw_playfield():
    fill_rect(PLAY_X, PLAY_Y, PLAY_W, PLAY_H, BLACK)
    outline_rect(0, PLAY_Y, WIDTH, PLAY_H, BORDER, 2)
    fill_rect(0, 288, WIDTH, 32, DARK_BG)
    draw_text("Swipe right at edge to exit", 12, 298, MUTED, DARK_BG, 216)


def draw_cell(cell, colour, inset=1):
    x, y = cell
    fill_rect(
        PLAY_X + x * GRID_SIZE + inset,
        PLAY_Y + y * GRID_SIZE + inset,
        GRID_SIZE - inset * 2,
        GRID_SIZE - inset * 2,
        colour
    )


def poll_game_gesture():
    # A non-blocking gesture collector suitable for the game loop.
    first = read_touch()
    if first is None:
        return None

    start = first
    end = first
    missing = 0

    while True:
        point = read_touch()
        if point is not None:
            end = point
            missing = 0
        else:
            missing += 1
            if missing >= 2:
                break
        time.sleep_ms(5)

    dx = end[0] - start[0]
    dy = end[1] - start[1]

    if abs(dx) >= 24 and abs(dx) > abs(dy):
        return "LEFT" if dx < 0 else "RIGHT"
    if abs(dy) >= 24 and abs(dy) > abs(dx):
        return "UP" if dy < 0 else "DOWN"
    return "TAP"


def game_over_screen(score):
    fill_rect(20, 112, 200, 104, CARD)
    outline_rect(20, 112, 200, 104, RED, 3)
    draw_text("GAME OVER", 76, 130, RED, CARD, 96)
    draw_text("SCORE: {}".format(score), 76, 158, YELLOW, CARD, 112)
    draw_text("Tap: retry", 68, 184, WHITE, CARD, 104)
    draw_text("Swipe right: menu", 48, 202, MUTED, CARD, 152)

    while True:
        gesture = capture_gesture()
        if gesture is None:
            continue
        kind = gesture[0]
        if kind == "RIGHT":
            return "MENU"
        if kind == "TAP":
            return "RETRY"


def run_snake_game():
    global screen_mode
    screen_mode = "SNAKE"

    while True:
        snake = [(8, 10), (7, 10), (6, 10)]
        direction = (1, 0)
        pending_direction = direction
        food = random_food(snake)
        score = 0

        fill_screen(BLACK)
        draw_snake_header(score)
        draw_playfield()
        for segment in snake:
            draw_cell(segment, SNAKE_GREEN)
        draw_cell(food, FOOD_RED, 2)

        last_step = time.ticks_ms()
        game_running = True

        while game_running:
            gesture = poll_game_gesture()

            if gesture == "UP" and direction != (0, 1):
                pending_direction = (0, -1)
            elif gesture == "DOWN" and direction != (0, -1):
                pending_direction = (0, 1)
            elif gesture == "LEFT" and direction != (1, 0):
                pending_direction = (-1, 0)
            elif gesture == "RIGHT" and direction != (-1, 0):
                pending_direction = (1, 0)

            now = time.ticks_ms()
            if time.ticks_diff(now, last_step) < SNAKE_STEP_MS:
                time.sleep_ms(5)
                continue

            last_step = now
            direction = pending_direction
            head_x, head_y = snake[0]
            new_head = (
                head_x + direction[0],
                head_y + direction[1]
            )

            # Collision with walls or self
            if (new_head[0] < 0 or new_head[0] >= COLS or
                    new_head[1] < 0 or new_head[1] >= ROWS or
                    new_head in snake):
                game_running = False
                break

            snake.insert(0, new_head)
            draw_cell(new_head, SNAKE_GREEN)

            if new_head == food:
                score += 1
                draw_snake_header(score)
                food = random_food(snake)
                draw_cell(food, FOOD_RED, 2)
            else:
                tail = snake.pop()
                draw_cell(tail, BLACK, 0)

        result = game_over_screen(score)
        if result == "MENU":
            draw_games_menu()
            return
        # RETRY loops and creates a fresh game.

# =========================================================
# TIC-TAC-TOE: LOCAL TWO-PLAYER GAME
# =========================================================

TTT_BOARD_X = 21
TTT_BOARD_Y = 66
TTT_CELL = 66
TTT_BOARD_SIZE = TTT_CELL * 3


def ttt_draw_grid():
    fill_screen(DARK_BG)
    fill_rect(0, 0, WIDTH, 48, HEADER)
    draw_text("< TIC TAC TOE", 8, 5, WHITE, HEADER, 128)
    draw_text("2 PLAYER", 160, 5, CYAN, HEADER, 72)
    draw_text("Player X starts", 60, 27, YELLOW, HEADER, 120)

    fill_rect(TTT_BOARD_X, TTT_BOARD_Y,
              TTT_BOARD_SIZE, TTT_BOARD_SIZE, BLACK)
    outline_rect(TTT_BOARD_X, TTT_BOARD_Y,
                 TTT_BOARD_SIZE, TTT_BOARD_SIZE, WHITE, 2)

    for index in (1, 2):
        x = TTT_BOARD_X + index * TTT_CELL
        y = TTT_BOARD_Y + index * TTT_CELL
        fill_rect(x - 1, TTT_BOARD_Y, 3, TTT_BOARD_SIZE, BORDER)
        fill_rect(TTT_BOARD_X, y - 1, TTT_BOARD_SIZE, 3, BORDER)

    fill_rect(0, 278, WIDTH, 42, DARK_BG)
    draw_text("Tap an empty square", 44, 282, MUTED, DARK_BG, 160)
    draw_text("Top-left < returns", 48, 300, MUTED, DARK_BG, 152)


def ttt_draw_x(row, column):
    x0 = TTT_BOARD_X + column * TTT_CELL + 13
    y0 = TTT_BOARD_Y + row * TTT_CELL + 13
    size = TTT_CELL - 26

    for offset in range(0, size, 3):
        fill_rect(x0 + offset, y0 + offset, 4, 4, TICTAC_RED)
        fill_rect(x0 + size - 1 - offset, y0 + offset, 4, 4, TICTAC_RED)


def ttt_draw_o(row, column):
    x0 = TTT_BOARD_X + column * TTT_CELL + 13
    y0 = TTT_BOARD_Y + row * TTT_CELL + 13
    size = TTT_CELL - 26
    thickness = 5

    # Square-ring O keeps rendering fast with the raw display driver.
    outline_rect(x0, y0, size, size, TICTAC_BLUE, thickness)


def ttt_show_turn(player):
    fill_rect(0, 24, WIDTH, 24, HEADER)
    colour = TICTAC_RED if player == "X" else TICTAC_BLUE
    draw_text("Player {} turn".format(player), 68, 27,
              colour, HEADER, 112)


def ttt_winner(board):
    lines = (
        ((0, 0), (0, 1), (0, 2)),
        ((1, 0), (1, 1), (1, 2)),
        ((2, 0), (2, 1), (2, 2)),
        ((0, 0), (1, 0), (2, 0)),
        ((0, 1), (1, 1), (2, 1)),
        ((0, 2), (1, 2), (2, 2)),
        ((0, 0), (1, 1), (2, 2)),
        ((0, 2), (1, 1), (2, 0))
    )

    for line in lines:
        a = board[line[0][0]][line[0][1]]
        b = board[line[1][0]][line[1][1]]
        c = board[line[2][0]][line[2][1]]
        if a != "" and a == b and b == c:
            return a, line

    for row in board:
        for value in row:
            if value == "":
                return None, None

    return "DRAW", None


def ttt_highlight_line(line):
    if line is None:
        return

    for row, column in line:
        x = TTT_BOARD_X + column * TTT_CELL + 4
        y = TTT_BOARD_Y + row * TTT_CELL + 4
        outline_rect(x, y, TTT_CELL - 8, TTT_CELL - 8,
                     WIN_GREEN, 4)


def ttt_result_panel(result):
    fill_rect(24, 120, 192, 88, CARD)
    outline_rect(24, 120, 192, 88, WIN_GREEN, 3)

    if result == "DRAW":
        draw_text("DRAW GAME", 80, 136, YELLOW, CARD, 88)
    else:
        draw_text("PLAYER {} WINS".format(result), 60, 136,
                  WIN_GREEN, CARD, 128)

    draw_text("Tap: play again", 60, 164, WHITE, CARD, 128)
    draw_text("Swipe right: Games", 44, 184, MUTED, CARD, 152)

    while True:
        gesture = capture_gesture()
        if gesture is None:
            continue
        if gesture[0] == "RIGHT":
            return "MENU"
        if gesture[0] == "TAP":
            return "RETRY"


def run_tic_tac_toe():
    global screen_mode
    screen_mode = "TIC_TAC_TOE"

    while True:
        board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""]
        ]
        player = "X"
        ttt_draw_grid()
        ttt_show_turn(player)

        while True:
            gesture = capture_gesture()
            if gesture is None:
                continue

            kind, x, y = gesture

            # Return to Games from the top-left back area.
            if ((kind == "TAP" and x < 58 and y < 55) or
                    kind == "RIGHT"):
                draw_games_menu()
                return

            if kind != "TAP":
                continue

            if not (TTT_BOARD_X <= x < TTT_BOARD_X + TTT_BOARD_SIZE and
                    TTT_BOARD_Y <= y < TTT_BOARD_Y + TTT_BOARD_SIZE):
                continue

            column = (x - TTT_BOARD_X) // TTT_CELL
            row = (y - TTT_BOARD_Y) // TTT_CELL

            if board[row][column] != "":
                continue

            board[row][column] = player

            if player == "X":
                ttt_draw_x(row, column)
            else:
                ttt_draw_o(row, column)

            result, winning_line = ttt_winner(board)

            if result is not None:
                ttt_highlight_line(winning_line)
                action = ttt_result_panel(result)
                if action == "MENU":
                    draw_games_menu()
                    return
                break

            player = "O" if player == "X" else "X"
            ttt_show_turn(player)

        # Result-panel RETRY reaches here and starts a fresh board.


# =========================================================
# MAIN
# =========================================================

print()
print("================================")
print("KeychainOS Swipe Menu + Snake")
print("================================")

gc.collect()
print("Free memory:", gc.mem_free())

init_display()

if not init_touch():
    fill_screen(RED)
    print("Touch controller not found")
    while True:
        time.sleep(1)

draw_home()

while True:
    gesture = capture_gesture()
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
            handle_home_tap(x, y)

    elif screen_mode == "GAMES":
        if kind == "LEFT":
            games_index = (games_index + 1) % len(GAME_APPS)
            draw_games_menu()
        elif kind == "RIGHT":
            # A short swipe changes cards. The game screens retain their
            # existing back behaviour after launch.
            games_index = (games_index - 1) % len(GAME_APPS)
            draw_games_menu()
        elif kind == "DOWN":
            draw_home()
        elif kind == "TAP":
            handle_games_tap(x, y)

    elif screen_mode in ("FILES_PLACEHOLDER", "PLACEHOLDER"):
        if kind == "RIGHT" or (kind == "TAP" and y < 42):
            draw_home()
