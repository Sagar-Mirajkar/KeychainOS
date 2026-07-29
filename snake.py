"""Snake game for KeychainOS with Nokia-style wall wraparound."""

import random
import time

GAME_NAME = "SNAKE"

GRID_SIZE = 12
PLAY_X = 0
PLAY_Y = 48
PLAY_WIDTH = 240
PLAY_HEIGHT = 240
COLUMNS = PLAY_WIDTH // GRID_SIZE
ROWS = PLAY_HEIGHT // GRID_SIZE

STARTING_SPEED_MS = 180
MINIMUM_SPEED_MS = 75
SPEED_INCREASE_MS = 5

BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
CYAN = 0x07FF
YELLOW = 0xFFE0
DARK_BACKGROUND = 0x0841
HEADER = 0x021F
CARD = 0x18E3
BORDER = 0x528A
MUTED = 0xA514
SNAKE_GREEN = 0x07E0
SNAKE_HEAD = 0xFFE0
FOOD_RED = 0xF800


def get_functions(context):
    required = (
        "fill_rect",
        "fill_screen",
        "draw_text",
        "outline_rect",
        "capture_gesture",
        "poll_gesture",
    )

    functions = {}

    for name in required:
        function = context.get(name)
        if function is None:
            raise ValueError("Snake missing context: " + name)
        functions[name] = function

    return functions


def create_food(snake):
    if len(snake) >= COLUMNS * ROWS:
        return None

    while True:
        position = (
            random.randrange(COLUMNS),
            random.randrange(ROWS),
        )

        if position not in snake:
            return position


def draw_cell(fill_rect, cell, colour, inset=1):
    column, row = cell

    fill_rect(
        PLAY_X + column * GRID_SIZE + inset,
        PLAY_Y + row * GRID_SIZE + inset,
        GRID_SIZE - inset * 2,
        GRID_SIZE - inset * 2,
        colour,
    )


def clear_cell(fill_rect, cell):
    draw_cell(fill_rect, cell, BLACK, 0)


def draw_header(fill_rect, draw_text, score):
    fill_rect(0, 0, 240, 48, HEADER)
    draw_text("< SNAKE", 8, 5, WHITE, HEADER, 72)
    draw_text("SCORE {}".format(score), 144, 5, YELLOW, HEADER, 88)
    draw_text("Walls wrap around", 52, 27, CYAN, HEADER, 136)


def draw_playfield(fill_rect, outline_rect, draw_text):
    fill_rect(PLAY_X, PLAY_Y, PLAY_WIDTH, PLAY_HEIGHT, BLACK)
    outline_rect(PLAY_X, PLAY_Y, PLAY_WIDTH, PLAY_HEIGHT, BORDER, 2)
    fill_rect(0, 288, 240, 32, DARK_BACKGROUND)
    draw_text("Swipe to steer", 64, 298, MUTED, DARK_BACKGROUND, 120)


def draw_initial_state(functions, snake, food, score):
    fill_screen = functions["fill_screen"]
    fill_rect = functions["fill_rect"]
    draw_text = functions["draw_text"]
    outline_rect = functions["outline_rect"]

    fill_screen(BLACK)
    draw_header(fill_rect, draw_text, score)
    draw_playfield(fill_rect, outline_rect, draw_text)

    for index in range(len(snake) - 1, -1, -1):
        colour = SNAKE_HEAD if index == 0 else SNAKE_GREEN
        draw_cell(fill_rect, snake[index], colour)

    if food is not None:
        draw_cell(fill_rect, food, FOOD_RED, 2)


def update_direction(gesture, current_direction, pending_direction):
    if gesture == "UP" and current_direction != (0, 1):
        return (0, -1)
    if gesture == "DOWN" and current_direction != (0, -1):
        return (0, 1)
    if gesture == "LEFT" and current_direction != (1, 0):
        return (-1, 0)
    if gesture == "RIGHT" and current_direction != (-1, 0):
        return (1, 0)
    return pending_direction


def wrapped_head(current_head, direction):
    """Move one step and wrap across every playfield edge."""
    return (
        (current_head[0] + direction[0]) % COLUMNS,
        (current_head[1] + direction[1]) % ROWS,
    )


def self_collision(new_head, snake, growing):
    """Walls are harmless; only collision with the snake ends the round."""
    body_to_check = snake if growing else snake[:-1]
    return new_head in body_to_check


def show_result(functions, score):
    fill_rect = functions["fill_rect"]
    draw_text = functions["draw_text"]
    outline_rect = functions["outline_rect"]
    capture_gesture = functions["capture_gesture"]

    fill_rect(20, 108, 200, 112, CARD)
    outline_rect(20, 108, 200, 112, RED, 3)
    draw_text("GAME OVER", 76, 126, RED, CARD, 96)
    draw_text("SCORE: {}".format(score), 76, 154, YELLOW, CARD, 112)
    draw_text("Tap: retry", 68, 181, WHITE, CARD, 104)
    draw_text("Swipe right: exit", 44, 201, MUTED, CARD, 152)

    while True:
        gesture = capture_gesture()
        if gesture is None:
            time.sleep_ms(10)
            continue
        if gesture[0] == "RIGHT":
            return "EXIT"
        if gesture[0] == "TAP":
            return "RETRY"


def play_round(functions):
    fill_rect = functions["fill_rect"]
    draw_text = functions["draw_text"]
    poll_gesture = functions["poll_gesture"]

    snake = [(8, 10), (7, 10), (6, 10)]
    current_direction = (1, 0)
    pending_direction = current_direction
    score = 0
    speed_ms = STARTING_SPEED_MS
    food = create_food(snake)

    draw_initial_state(functions, snake, food, score)
    last_step_time = time.ticks_ms()

    while True:
        gesture = poll_gesture()
        if gesture is not None:
            pending_direction = update_direction(
                gesture,
                current_direction,
                pending_direction,
            )

        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_step_time) < speed_ms:
            time.sleep_ms(5)
            continue

        last_step_time = current_time
        current_direction = pending_direction

        # Nokia-style edge behaviour: modulo wraps left/right/top/bottom.
        new_head = wrapped_head(snake[0], current_direction)
        growing = food is not None and new_head == food

        if self_collision(new_head, snake, growing):
            return show_result(functions, score)

        draw_cell(fill_rect, snake[0], SNAKE_GREEN)
        snake.insert(0, new_head)
        draw_cell(fill_rect, new_head, SNAKE_HEAD)

        if growing:
            score += 1
            speed_ms = max(
                MINIMUM_SPEED_MS,
                STARTING_SPEED_MS - score * SPEED_INCREASE_MS,
            )
            draw_header(fill_rect, draw_text, score)
            food = create_food(snake)

            if food is None:
                return show_result(functions, score)

            draw_cell(fill_rect, food, FOOD_RED, 2)
        else:
            old_tail = snake.pop()
            clear_cell(fill_rect, old_tail)


def run(context):
    print("Starting Snake with wall wraparound")
    functions = get_functions(context)

    while True:
        result = play_round(functions)
        if result == "EXIT":
            print("Exiting Snake")
            return "EXIT"
