"""Two-player Tic-Tac-Toe game for KeychainOS."""

import time

GAME_NAME = "TIC TAC TOE"

BOARD_X = 21
BOARD_Y = 66
CELL_SIZE = 66
BOARD_SIZE = CELL_SIZE * 3

BLACK = 0x0000
WHITE = 0xFFFF
CYAN = 0x07FF
YELLOW = 0xFFE0
DARK_BG = 0x0841
HEADER = 0x021F
CARD = 0x18E3
BORDER = 0x528A
MUTED = 0xA514
PLAYER_X = 0xF960
PLAYER_O = 0x04FF
WIN_GREEN = 0x07E0


def create_board():
    return [
        ["", "", ""],
        ["", "", ""],
        ["", "", ""]
    ]


def draw_grid(display):
    display.fill(DARK_BG)
    display.fill_rect(0, 0, 240, 48, HEADER)
    display.fill_rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE, BLACK)
    display.outline_rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE, WHITE, 2)

    for index in (1, 2):
        x = BOARD_X + index * CELL_SIZE
        y = BOARD_Y + index * CELL_SIZE
        display.fill_rect(x - 1, BOARD_Y, 3, BOARD_SIZE, BORDER)
        display.fill_rect(BOARD_X, y - 1, BOARD_SIZE, 3, BORDER)


def draw_x(display, row, column):
    x0 = BOARD_X + column * CELL_SIZE + 13
    y0 = BOARD_Y + row * CELL_SIZE + 13
    size = CELL_SIZE - 26

    for offset in range(0, size, 3):
        display.fill_rect(x0 + offset, y0 + offset, 4, 4, PLAYER_X)
        display.fill_rect(x0 + size - 1 - offset, y0 + offset, 4, 4, PLAYER_X)


def draw_o(display, row, column):
    x0 = BOARD_X + column * CELL_SIZE + 13
    y0 = BOARD_Y + row * CELL_SIZE + 13
    size = CELL_SIZE - 26
    display.outline_rect(x0, y0, size, size, PLAYER_O, 5)


def check_result(board):
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
        first = board[line[0][0]][line[0][1]]
        second = board[line[1][0]][line[1][1]]
        third = board[line[2][0]][line[2][1]]

        if first != "" and first == second and second == third:
            return first, line

    for row in board:
        for value in row:
            if value == "":
                return None, None

    return "DRAW", None


def highlight_winner(display, line):
    if line is None:
        return

    for row, column in line:
        x = BOARD_X + column * CELL_SIZE + 4
        y = BOARD_Y + row * CELL_SIZE + 4
        display.outline_rect(x, y, CELL_SIZE - 8, CELL_SIZE - 8, WIN_GREEN, 4)


def wait_for_result_action(touch):
    while True:
        gesture = touch.capture_gesture()

        if gesture is None:
            time.sleep_ms(10)
            continue

        if gesture[0] == "RIGHT":
            return "EXIT"

        if gesture[0] == "TAP":
            return "RETRY"


def play_round(display, touch):
    board = create_board()
    player = "X"
    draw_grid(display)

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

        if not (
            BOARD_X <= x < BOARD_X + BOARD_SIZE
            and BOARD_Y <= y < BOARD_Y + BOARD_SIZE
        ):
            continue

        column = (x - BOARD_X) // CELL_SIZE
        row = (y - BOARD_Y) // CELL_SIZE

        if board[row][column] != "":
            continue

        board[row][column] = player

        if player == "X":
            draw_x(display, row, column)
        else:
            draw_o(display, row, column)

        result, winning_line = check_result(board)

        if result is not None:
            highlight_winner(display, winning_line)
            return wait_for_result_action(touch)

        player = "O" if player == "X" else "X"


def run(display, touch):
    """Run Tic-Tac-Toe and return EXIT when leaving the game."""

    print("Starting two-player Tic-Tac-Toe")

    while True:
        result = play_round(display, touch)

        if result == "EXIT":
            print("Exiting Tic-Tac-Toe")
            return "EXIT"
