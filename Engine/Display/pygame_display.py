import pygame
import sys
import numpy as np

ROWS = 6
COLS = 7
CELL_SIZE = 80
MARGIN = 10
ABOVE_BOARD_HEIGHT = 120  # Space for disk hoverpreview and legend at the top
BELOW_BOARD_HEIGHT = 100  # Space at bottom for messages
BOARD_WIDTH = 2 * MARGIN + COLS * CELL_SIZE  # Left margin + cells + right margin
BOARD_HEIGHT = 2 * MARGIN + ROWS * CELL_SIZE  # Top margin + cells + bottom margin
WINDOW_WIDTH = BOARD_WIDTH
WINDOW_HEIGHT = ABOVE_BOARD_HEIGHT + BOARD_HEIGHT + BELOW_BOARD_HEIGHT

# Colors
BLUE = (0, 100, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)


def create_board():
    """Initialize pygame and create the game window"""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Connect 4")
    font = pygame.font.Font(None, 36)
    return screen, font


def print_board(screen, font, obs, message="", current_agent=None, player_turn=None, hover_col=None):
    """Draw the current board state using pygame - redrawn every frame"""
    screen.fill(WHITE)

    # Convert observation to board state
    planes = obs["observation"]
    current_player_disks = planes[:, :, 0]  # Player disks
    other_player_disks = planes[:, :, 1]  # Computer disks

    # Draw legend at the top, centered horizontally
    legend_y = 20
    legend_spacing = 100
    legend_center_x = WINDOW_WIDTH // 2

    # Computer legend (Red)
    computer_x = legend_center_x - legend_spacing // 2
    pygame.draw.circle(screen, RED, (computer_x - 70, legend_y), 15)
    pygame.draw.circle(screen, BLACK, (computer_x - 70, legend_y), 15, 1)
    computer_text = pygame.font.Font(None, 24).render("Computer", True, BLACK)
    screen.blit(computer_text, (computer_x - 45, legend_y - 10))

    # Player legend (Yellow)
    player_x = legend_center_x + legend_spacing // 2
    pygame.draw.circle(screen, YELLOW, (player_x - 25, legend_y), 15)
    pygame.draw.circle(screen, BLACK, (player_x - 25, legend_y), 15, 1)
    player_text = pygame.font.Font(None, 24).render("You", True, BLACK)
    screen.blit(player_text, (player_x, legend_y - 10))

    # Draw disk if hovering over a column
    if hover_col is not None:
        center_x = MARGIN + hover_col * CELL_SIZE + CELL_SIZE // 2
        center_y = ABOVE_BOARD_HEIGHT - (CELL_SIZE // 2)
        radius = CELL_SIZE // 2 - 5
        # Hover disk color is yellow for player, red for computer
        if current_agent == player_turn:
            hover_color = YELLOW
        else:
            hover_color = RED
        pygame.draw.circle(screen, hover_color, (center_x, center_y), radius)
        pygame.draw.circle(screen, BLACK, (center_x, center_y), radius, 2)

    # Draw the blue board background
    board_rect = pygame.Rect(0, ABOVE_BOARD_HEIGHT, BOARD_WIDTH, BOARD_HEIGHT)
    pygame.draw.rect(screen, BLUE, board_rect)
    # Draw circles for each cell (each slot might be filled or empty - again this is redrawn every frame)
    for row in range(ROWS):
        for col in range(COLS):
            center_x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
            center_y = ABOVE_BOARD_HEIGHT + MARGIN + row * CELL_SIZE + CELL_SIZE // 2
            radius = CELL_SIZE // 2 - 5

            # Determine disk color - Computer = RED, Player = YELLOW, empty = WHITE
            if current_agent == player_turn:
                # Current agent is the human player
                if current_player_disks[row, col] == 1:
                    color = YELLOW
                elif other_player_disks[row, col] == 1:
                    color = RED
                else:
                    color = WHITE
            else:
                # Current agent is the computer
                if current_player_disks[row, col] == 1:
                    color = RED
                elif other_player_disks[row, col] == 1:
                    color = YELLOW
                else:
                    color = WHITE

            # Draw the disk
            pygame.draw.circle(screen, color, (center_x, center_y), radius)
            pygame.draw.circle(screen, BLACK, (center_x, center_y), radius, 2)

    # Draw column numbers below the board
    column_font = pygame.font.Font(None, 28)
    for col in range(COLS):
        center_x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
        col_text = column_font.render(str(col), True, BLACK)
        text_rect = col_text.get_rect(center=(center_x, ABOVE_BOARD_HEIGHT + BOARD_HEIGHT + 20))
        screen.blit(col_text, text_rect)

    # Print message below the board
    if message:
        message_font = pygame.font.Font(None, 40)
        text = message_font.render(message, True, BLACK)
        message_y = ABOVE_BOARD_HEIGHT + BOARD_HEIGHT + 25 + (BELOW_BOARD_HEIGHT - 25) // 2
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, message_y))
        screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()


def handle_pygame_events():
    """Handle pygame events to keep window responsive"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


def get_player_move_from_pygame(screen, font, obs, legal_cols, current_agent, player_turn):
    """Get player move by clicking on the pygame board with hover preview and drop animation"""
    waiting_for_move = True
    selected_col = None
    current_hover_col = None

    while waiting_for_move:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Determine hover column
        hover_col = None
        if 0 <= mouse_x <= BOARD_WIDTH and 0 <= mouse_y <= ABOVE_BOARD_HEIGHT + BOARD_HEIGHT:
            col = (mouse_x - MARGIN) // CELL_SIZE
            if 0 <= col < COLS and col in legal_cols:
                hover_col = col

        # Only redraw if hover state changed
        if hover_col != current_hover_col:
            current_hover_col = hover_col
            print_board(screen, font, obs, f"Your turn!", current_agent, player_turn, current_hover_col)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Calculate which column was clicked
            elif event.type == pygame.MOUSEBUTTONDOWN:
                col = (mouse_x - MARGIN) // CELL_SIZE
                if 0 <= col < COLS and col in legal_cols:
                    selected_col = col
                    waiting_for_move = False

        pygame.time.wait(16) # Approx 60 FPS - limited refresh rate to reduce CPU usage

    return selected_col


def animate_disk_drop(screen, font, obs, col, current_agent, player_turn):
    """Animate a disk dropping from the hover area to its final position"""

    planes = obs["observation"]
    current_player_disks = planes[:, :, 0]
    other_player_disks = planes[:, :, 1]

    # Find the lowest empty row in this column for the disk to land
    target_row = ROWS - 1
    for row in range(ROWS):
        if current_player_disks[row, col] == 1 or other_player_disks[row, col] == 1:
            target_row = row - 1
            break

    # Animation start parameters
    center_x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
    start_y = ABOVE_BOARD_HEIGHT - (CELL_SIZE // 2)
    end_y = ABOVE_BOARD_HEIGHT + MARGIN + target_row * CELL_SIZE + CELL_SIZE // 2
    radius = CELL_SIZE // 2 - 5

    # disk color
    if current_agent == player_turn:
        disk_color = YELLOW
    else:
        disk_color = RED

    # The animation:
    animation_frames = 35
    for frame in range(animation_frames):
        # Eased animation (starts slow, accelerates)
        progress = frame / (animation_frames - 1)
        eased_progress = progress * progress
        current_y = start_y + (end_y - start_y) * eased_progress

        if current_agent == player_turn:
            print_board(screen, font, obs, f"You chose column {col}.", current_agent, player_turn)
        else:
            print_board(screen, font, obs, f"Computer chose column {col}.", current_agent, player_turn)

        # Draw the falling disk
        pygame.draw.circle(screen, disk_color, (int(center_x), int(current_y)), radius)
        pygame.draw.circle(screen, BLACK, (int(center_x), int(current_y)), radius, 2)
        pygame.display.flip()

        pygame.time.wait(16) # 60 FPS animation speed


def animate_computer_move(screen, font, obs, col, current_agent, player_turn):
    """Show computer's intended move with preview, then animate the drop"""
    # First show the computer's disk in the hover area for 1 second (around 30 frames)
    center_x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
    center_y = ABOVE_BOARD_HEIGHT - (CELL_SIZE // 2)
    radius = CELL_SIZE // 2 - 5
    disk_color = RED

    print_board(screen, font, obs, f"Computer chose column {col}.", current_agent, player_turn)

    # Draw the preview disk in hover area
    pygame.draw.circle(screen, disk_color, (center_x, center_y), radius)
    pygame.draw.circle(screen, BLACK, (center_x, center_y), radius, 2)
    pygame.display.flip()

    pygame.time.wait(30)

    # Now do the drop animation (same as player)
    animate_disk_drop(screen, font, obs, col, current_agent, player_turn)