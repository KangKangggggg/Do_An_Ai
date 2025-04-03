import pygame
import random
import sys
import time
import math
import os
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700  # Increased height for buttons
GRID_SIZE = 8
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE
BUTTON_HEIGHT = 50
GAME_AREA_HEIGHT = WINDOW_HEIGHT - BUTTON_HEIGHT
FPS = 60

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
LEVEL_COMPLETE = 3
GAME_OVER = 4

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
CANDY_COLORS = [
    (255, 0, 0),     # Red
    (0, 255, 0),     # Green
    (0, 0, 255),     # Blue
    (255, 255, 0),   # Yellow
    (255, 0, 255),   # Purple
    (0, 255, 255),   # Cyan
]

# Special candy types
STRIPED_HORIZONTAL_START = 100  # Use large numbers to avoid conflicts
STRIPED_VERTICAL_START = 200
WRAPPED_START = 300
COLOR_BOMB = 400

# Set up the window
DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Candy Crush Clone')
CLOCK = pygame.time.Clock()

# Load sounds
try:
    MATCH_SOUND = pygame.mixer.Sound('match.wav')
    SPECIAL_SOUND = pygame.mixer.Sound('special.wav')
    COMBO_SOUND = pygame.mixer.Sound('combo.wav')
    LEVEL_COMPLETE_SOUND = pygame.mixer.Sound('level_complete.wav')
    GAME_OVER_SOUND = pygame.mixer.Sound('game_over.wav')
except:
    # Create placeholder sounds if files not found
    MATCH_SOUND = pygame.mixer.Sound(buffer=bytes(bytearray([0] * 44)))
    SPECIAL_SOUND = pygame.mixer.Sound(buffer=bytes(bytearray([0] * 44)))
    COMBO_SOUND = pygame.mixer.Sound(buffer=bytes(bytearray([0] * 44)))
    LEVEL_COMPLETE_SOUND = pygame.mixer.Sound(buffer=bytes(bytearray([0] * 44)))
    GAME_OVER_SOUND = pygame.mixer.Sound(buffer=bytes(bytearray([0] * 44)))
    print("Sound files not found. Using silent placeholders.")

# Game variables
board = []
animation_board = []  # For smooth animations
selected_candy = None
score = 0
total_score = 0
current_level = 1
target_score = 1000  # Target score to complete the level
moves_left = 20      # Number of moves allowed
game_state = MENU
hint_timer = 0
hint_candy = None
last_action_time = 0
animations = []  # List to store active animations

# Level configuration
level_config = [
    # Level 1
    {"target_score": 1000, "moves": 20, "grid_size": 8},
    # Level 2
    {"target_score": 2000, "moves": 18, "grid_size": 8},
    # Level 3
    {"target_score": 3000, "moves": 16, "grid_size": 8},
    # Level 4
    {"target_score": 4000, "moves": 15, "grid_size": 8},
    # Level 5
    {"target_score": 5000, "moves": 14, "grid_size": 8},
]

# Fonts
title_font = pygame.font.SysFont('Arial', 48, bold=True)
button_font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)
score_font = pygame.font.SysFont('Arial', 36, bold=True)

# Animation class
class Animation:
    def __init__(self, anim_type, start_pos, end_pos=None, duration=0.3, color=None, size=None):
        self.type = anim_type  # 'swap', 'fall', 'match', 'special'
        self.start_pos = start_pos
        self.end_pos = end_pos if end_pos else start_pos
        self.start_time = time.time()
        self.duration = duration
        self.color = color
        self.size = size
        self.completed = False
    
    def update(self):
        current_time = time.time()
        progress = (current_time - self.start_time) / self.duration
        
        if progress >= 1.0:
            self.completed = True
            return True
        
        return False
    
    def get_current_position(self):
        if self.completed:
            return self.end_pos
            
        progress = min(1.0, (time.time() - self.start_time) / self.duration)
        
        # Ease out function for smoother animation
        progress = 1 - (1 - progress) ** 2
        
        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos
        
        current_row = start_row + (end_row - start_row) * progress
        current_col = start_col + (end_col - start_col) * progress
        
        return (current_row, current_col)

# Helper function to get base candy color
def get_base_color(candy_type):
    if candy_type < STRIPED_HORIZONTAL_START:
        return candy_type  # Regular candy
    elif candy_type < STRIPED_VERTICAL_START:
        return candy_type - STRIPED_HORIZONTAL_START  # Horizontal striped
    elif candy_type < WRAPPED_START:
        return candy_type - STRIPED_VERTICAL_START  # Vertical striped
    elif candy_type < COLOR_BOMB:
        return candy_type - WRAPPED_START  # Wrapped
    return -1  # Color bomb has no base color

# Button class
class Button:
    def __init__(self, x, y, width, height, text, icon=None, color=LIGHT_GRAY, hover_color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self):
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(DISPLAY_SURF, color, self.rect)
        pygame.draw.rect(DISPLAY_SURF, BLACK, self.rect, 2)  # Border
        
        # Draw text
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        DISPLAY_SURF.blit(text_surf, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

# Create buttons
def create_buttons():
    buttons = {}
    
    # Main menu buttons
    buttons['play'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, 200, 50, "▶️ Play")
    
    # Game buttons
    button_width = WINDOW_WIDTH // 7
    
    buttons['score'] = Button(0, GAME_AREA_HEIGHT, button_width, BUTTON_HEIGHT, "🎯 Score")
    buttons['moves'] = Button(button_width, GAME_AREA_HEIGHT, button_width, BUTTON_HEIGHT, "🔢 Moves")
    buttons['goal'] = Button(button_width*2, GAME_AREA_HEIGHT, button_width, BUTTON_HEIGHT, "🎯 Goal")
    buttons['hint'] = Button(button_width*3, GAME_AREA_HEIGHT, button_width, BUTTON_HEIGHT, "💡 Hint")
    buttons['shuffle'] = Button(button_width*4, GAME_AREA_HEIGHT, button_width, BUTTON_HEIGHT, "🔄 Shuffle")
    buttons['pause'] = Button(button_width*5, GAME_AREA_HEIGHT, button_width*2, BUTTON_HEIGHT, "⏸️ Pause")
    
    # Pause menu buttons
    buttons['resume'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 60, 200, 50, "▶️ Resume")
    buttons['restart'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, 200, 50, "🔄 Restart")
    buttons['quit'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 60, 200, 50, "❌ Quit")
    
    # Level complete buttons
    buttons['next_level'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 30, 200, 50, "▶️ Next Level")
    buttons['menu'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 90, 200, 50, "🏠 Main Menu")
    
    # Game over buttons
    buttons['try_again'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 30, 200, 50, "🔄 Try Again")
    
    return buttons

buttons = create_buttons()

def initialize_board():
    """Create a new game board filled with random candies"""
    global board, animation_board, score, moves_left, game_state, hint_candy, last_action_time, animations, target_score
    
    # Set level configuration
    level_data = level_config[min(current_level - 1, len(level_config) - 1)]
    target_score = level_data["target_score"]
    moves_left = level_data["moves"]
    
    # Create the board
    board = []
    for _ in range(GRID_SIZE):
        row = []
        for _ in range(GRID_SIZE):
            row.append(random.randint(0, len(CANDY_COLORS) - 1))
        board.append(row)
    
    # Initialize animation board
    animation_board = []
    for row in range(GRID_SIZE):
        anim_row = []
        for col in range(GRID_SIZE):
            anim_row.append((row, col))  # Initial position is the same as board position
        animation_board.append(anim_row)
    
    # Check for matches at the start and resolve them
    while check_for_matches()[0]:
        resolve_matches()
        fill_board()
    
    # Reset game variables
    score = 0
    hint_candy = None
    last_action_time = time.time()
    animations = []
    game_state = PLAYING

def draw_candy(row, col, pos=None):
    """Draw a candy at the specified position"""
    candy_type = board[row][col]
    if candy_type == -1:
        return  # Don't draw empty spaces
    
    # Use animation position if provided, otherwise use board position
    if pos:
        center_y, center_x = pos
    else:
        center_x = col * CELL_SIZE + CELL_SIZE // 2
        center_y = row * CELL_SIZE + CELL_SIZE // 2
        
    radius = CELL_SIZE // 2 - 5
    
    if candy_type < STRIPED_HORIZONTAL_START:
        # Regular candy
        pygame.draw.circle(
            DISPLAY_SURF, 
            CANDY_COLORS[candy_type], 
            (center_x, center_y), 
            radius
        )
    elif candy_type < STRIPED_VERTICAL_START:
        # Horizontal striped candy
        base_color = get_base_color(candy_type)
        pygame.draw.circle(
            DISPLAY_SURF, 
            CANDY_COLORS[base_color], 
            (center_x, center_y), 
            radius
        )
        # Draw horizontal stripes
        for y_offset in range(-radius + 3, radius - 2, 5):
            pygame.draw.line(
                DISPLAY_SURF, 
                WHITE, 
                (center_x - radius + 3, center_y + y_offset), 
                (center_x + radius - 3, center_y + y_offset), 
                2
            )
    elif candy_type < WRAPPED_START:
        # Vertical striped candy
        base_color = get_base_color(candy_type)
        pygame.draw.circle(
            DISPLAY_SURF, 
            CANDY_COLORS[base_color], 
            (center_x, center_y), 
            radius
        )
        # Draw vertical stripes
        for x_offset in range(-radius + 3, radius - 2, 5):
            pygame.draw.line(
                DISPLAY_SURF, 
                WHITE, 
                (center_x + x_offset, center_y - radius + 3), 
                (center_x + x_offset, center_y + radius - 3), 
                2
            )
    elif candy_type < COLOR_BOMB:
        # Wrapped candy
        base_color = get_base_color(candy_type)
        pygame.draw.circle(
            DISPLAY_SURF, 
            CANDY_COLORS[base_color], 
            (center_x, center_y), 
            radius
        )
        # Draw wrapper
        pygame.draw.circle(
            DISPLAY_SURF, 
            WHITE, 
            (center_x, center_y), 
            radius - 3, 
            2
        )
        pygame.draw.circle(
            DISPLAY_SURF, 
            WHITE, 
            (center_x, center_y), 
            radius, 
            2
        )
    elif candy_type == COLOR_BOMB:
        # Color bomb
        pygame.draw.circle(
            DISPLAY_SURF, 
            BLACK, 
            (center_x, center_y), 
            radius
        )
        # Draw sparkles
        for angle in range(0, 360, 45):
            x = center_x + int(radius * 0.7 * math.cos(math.radians(angle)))
            y = center_y + int(radius * 0.7 * math.sin(math.radians(angle)))
            pygame.draw.circle(
                DISPLAY_SURF, 
                WHITE, 
                (x, y), 
                2
            )

def draw_board():
    """Draw the game board and candies"""
    DISPLAY_SURF.fill(WHITE)
    
    # Draw grid lines
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(DISPLAY_SURF, BLACK, (x, 0), (x, GAME_AREA_HEIGHT), 1)
    for y in range(0, GAME_AREA_HEIGHT, CELL_SIZE):
        pygame.draw.line(DISPLAY_SURF, BLACK, (0, y), (WINDOW_WIDTH, y), 1)
    
    # Draw candies with animations
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] != -1:
                # Check if this candy has an active animation
                animated = False
                for anim in animations:
                    if anim.start_pos == (row, col) or anim.end_pos == (row, col):
                        if not anim.completed:
                            pos = anim.get_current_position()
                            # Convert board coordinates to pixel coordinates
                            pixel_pos = (pos[1] * CELL_SIZE + CELL_SIZE // 2, 
                                        pos[0] * CELL_SIZE + CELL_SIZE // 2)
                            draw_candy(row, col, pixel_pos)
                            animated = True
                            break
                
                # If no animation, draw normally
                if not animated:
                    draw_candy(row, col)
    
    # Draw match animations
    for anim in animations:
        if anim.type == 'match' and not anim.completed:
            progress = min(1.0, (time.time() - anim.start_time) / anim.duration)
            row, col = anim.start_pos
            center_x = col * CELL_SIZE + CELL_SIZE // 2
            center_y = row * CELL_SIZE + CELL_SIZE // 2
            
            # Fade out and expand
            alpha = int(255 * (1 - progress))
            size = int(CELL_SIZE * (0.5 + progress * 0.5))
            
            # Create a surface with per-pixel alpha
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*anim.color, alpha), (size//2, size//2), size//2)
            DISPLAY_SURF.blit(surf, (center_x - size//2, center_y - size//2))
    
    # Highlight selected candy
    if selected_candy:
        row, col = selected_candy
        pygame.draw.rect(
            DISPLAY_SURF, 
            (255, 255, 255), 
            (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 
            3
        )
    
    # Highlight hint candy if available
    if hint_candy and time.time() % 1 > 0.5:  # Blinking effect
        row1, col1, row2, col2 = hint_candy
        pygame.draw.rect(
            DISPLAY_SURF, 
            (255, 255, 0), 
            (col1 * CELL_SIZE, row1 * CELL_SIZE, CELL_SIZE, CELL_SIZE), 
            3
        )
        pygame.draw.rect(
            DISPLAY_SURF, 
            (255, 255, 0), 
            (col2 * CELL_SIZE, row2 * CELL_SIZE, CELL_SIZE, CELL_SIZE), 
            3
        )
    
    # Draw buttons
    mouse_pos = pygame.mouse.get_pos()
    
    if game_state == PLAYING:
        # Update button text with current values
        buttons['score'].text = f"🎯 {score}"
        buttons['moves'].text = f"🔢 {moves_left}"
        buttons['goal'].text = f"🎯 Goal: {target_score}"
        
        # Draw game buttons
        for button_name in ['score', 'moves', 'goal', 'hint', 'shuffle', 'pause']:
            buttons[button_name].update(mouse_pos)
            buttons[button_name].draw()
        
        # Draw level indicator
        level_text = small_font.render(f"Level: {current_level}", True, BLACK)
        DISPLAY_SURF.blit(level_text, (10, 10))
    
    elif game_state == MENU:
        # Draw title
        title_text = title_font.render("Candy Crush", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        DISPLAY_SURF.blit(title_text, title_rect)
        
        # Draw play button
        buttons['play'].update(mouse_pos)
        buttons['play'].draw()
        
        # Draw high score if available
        if total_score > 0:
            score_text = button_font.render(f"Total Score: {total_score}", True, BLACK)
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
            DISPLAY_SURF.blit(score_text, score_rect)
    
    elif game_state == PAUSED:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        DISPLAY_SURF.blit(overlay, (0, 0))
        
        # Draw pause menu title
        pause_text = title_font.render("Game Paused", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        DISPLAY_SURF.blit(pause_text, pause_rect)
        
        # Draw pause menu buttons
        for button_name in ['resume', 'restart', 'quit']:
            buttons[button_name].update(mouse_pos)
            buttons[button_name].draw()
    
    elif game_state == LEVEL_COMPLETE:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        DISPLAY_SURF.blit(overlay, (0, 0))
        
        # Draw level complete title
        complete_text = title_font.render("Level Complete!", True, (0, 255, 0))
        complete_rect = complete_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        DISPLAY_SURF.blit(complete_text, complete_rect)
        
        # Draw score
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3 + 20))
        DISPLAY_SURF.blit(score_text, score_rect)
        
        # Draw buttons
        for button_name in ['next_level', 'menu']:
            buttons[button_name].update(mouse_pos)
            buttons[button_name].draw()
    
    elif game_state == GAME_OVER:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        DISPLAY_SURF.blit(overlay, (0, 0))
        
        # Draw game over title
        over_text = title_font.render("Game Over", True, (255, 0, 0))
        over_rect = over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        DISPLAY_SURF.blit(over_text, over_rect)
        
        # Draw score
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3 + 20))
        DISPLAY_SURF.blit(score_text, score_rect)
        
        # Draw buttons
        for button_name in ['try_again', 'menu']:
            buttons[button_name].update(mouse_pos)
            buttons[button_name].draw()

def get_candy_at_pixel(x, y):
    """Convert pixel coordinates to board coordinates"""
    if y >= GAME_AREA_HEIGHT:
        return None
        
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    
    if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE:
        return None
    
    return (row, col)

def swap_candies(candy1, candy2):
    """Swap two candies on the board"""
    global animations
    
    row1, col1 = candy1
    row2, col2 = candy2
    
    # Add swap animation
    animations.append(Animation('swap', (row1, col1), (row2, col2), 0.3))
    animations.append(Animation('swap', (row2, col2), (row1, col1), 0.3))
    
    # Perform the swap
    board[row1][col1], board[row2][col2] = board[row2][col2], board[row1][col1]

def are_adjacent(candy1, candy2):
    """Check if two candies are adjacent"""
    row1, col1 = candy1
    row2, col2 = candy2
    
    return (abs(row1 - row2) == 1 and col1 == col2) or (abs(col1 - col2) == 1 and row1 == row2)

def check_for_matches():
    """Check for matches of 3 or more candies in a row or column"""
    matches = []
    match_positions = set()  # Keep track of all matched positions
    
    # Check horizontal matches
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 2):
            candy_type = get_base_color(board[row][col])
            if candy_type == -1:
                continue  # Skip color bombs or empty spaces
                
            if (get_base_color(board[row][col + 1]) == candy_type and 
                get_base_color(board[row][col + 2]) == candy_type):
                # Find how long this match is
                match_length = 3
                while (col + match_length < GRID_SIZE and 
                       get_base_color(board[row][col + match_length]) == candy_type):
                    match_length += 1
                
                # Add all positions in this match
                match = []
                for i in range(match_length):
                    match.append((row, col + i))
                    match_positions.add((row, col + i))
                matches.append(match)
    
    # Check vertical matches
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE - 2):
            candy_type = get_base_color(board[row][col])
            if candy_type == -1:
                continue  # Skip color bombs or empty spaces
                
            if (get_base_color(board[row + 1][col]) == candy_type and 
                get_base_color(board[row + 2][col]) == candy_type):
                # Find how long this match is
                match_length = 3
                while (row + match_length < GRID_SIZE and 
                       get_base_color(board[row + match_length][col]) == candy_type):
                    match_length += 1
                
                # Add all positions in this match
                match = []
                for i in range(match_length):
                    match.append((row + i, col))
                    match_positions.add((row + i, col))
                matches.append(match)
    
    return matches, match_positions

def detect_special_patterns(matches, match_positions):
    """Detect L, T and other special patterns from matches"""
    special_candies = []
    
    # Find intersections of matches (for L and T shapes)
    intersection_points = []
    for i in range(len(matches)):
        for j in range(i + 1, len(matches)):
            # Find common positions between two matches
            common_positions = set(matches[i]) & set(matches[j])
            for pos in common_positions:
                intersection_points.append(pos)
    
    # Process each match to determine special candy creation
    for match in matches:
        if len(match) == 4:
            # 4 in a row/column creates a striped candy
            row, col = match[0]  # Use the first position
            # Check if this is a horizontal or vertical match
            if all(pos[0] == row for pos in match):  # Horizontal
                special_candies.append(("striped_h", row, col))
            else:  # Vertical
                special_candies.append(("striped_v", row, col))
        elif len(match) >= 5:
            # 5 or more in a row/column creates a color bomb
            row, col = match[0]  # Use the first position
            special_candies.append(("color_bomb", row, col))
    
    # Check for L and T shapes at intersection points
    for row, col in intersection_points:
        # Check if this point is part of an L or T shape
        # by looking at the surrounding positions
        
        # Get the candy type at this position
        candy_type = get_base_color(board[row][col])
        
        # Check for L shape (horizontal + vertical line)
        horizontal_match = []
        vertical_match = []
        
        # Check horizontal line through this point
        left_count = 0
        for c in range(col - 1, -1, -1):
            if get_base_color(board[row][c]) == candy_type:
                left_count += 1
                horizontal_match.append((row, c))
            else:
                break
                
        right_count = 0
        for c in range(col + 1, GRID_SIZE):
            if get_base_color(board[row][c]) == candy_type:
                right_count += 1
                horizontal_match.append((row, c))
            else:
                break
        
        # Check vertical line through this point
        up_count = 0
        for r in range(row - 1, -1, -1):
            if get_base_color(board[r][col]) == candy_type:
                up_count += 1
                vertical_match.append((r, col))
            else:
                break
                
        down_count = 0
        for r in range(row + 1, GRID_SIZE):
            if get_base_color(board[r][col]) == candy_type:
                down_count += 1
                vertical_match.append((r, col))
            else:
                break
        
        # Check if we have an L or T shape
        horizontal_length = left_count + right_count + 1
        vertical_length = up_count + down_count + 1
        
        if (horizontal_length >= 3 and vertical_length >= 3):
            # We have an L or T shape, create a wrapped candy
            special_candies.append(("wrapped", row, col))
    
    return special_candies

def create_special_candy(candy_type, row, col):
    """Create a special candy at the specified position"""
    original_color = get_base_color(board[row][col])
    
    if candy_type == "striped_h":
        board[row][col] = STRIPED_HORIZONTAL_START + original_color
    elif candy_type == "striped_v":
        board[row][col] = STRIPED_VERTICAL_START + original_color
    elif candy_type == "wrapped":
        board[row][col] = WRAPPED_START + original_color
    elif candy_type == "color_bomb":
        board[row][col] = COLOR_BOMB

def activate_special_candy(row, col):
    """Activate the special candy at the specified position"""
    global score, animations
    candy_type = board[row][col]
    affected_cells = []
    
    if STRIPED_HORIZONTAL_START <= candy_type < STRIPED_VERTICAL_START:
        # Activate striped horizontal - clear entire row
        base_color = get_base_color(candy_type)
        for c in range(GRID_SIZE):
            if board[row][c] != -1:  # Don't clear already cleared cells
                affected_cells.append((row, c))
                # Add animation
                animations.append(Animation('match', (row, c), duration=0.5, 
                                           color=CANDY_COLORS[base_color]))
                
    elif STRIPED_VERTICAL_START <= candy_type < WRAPPED_START:
        # Activate striped vertical - clear entire column
        base_color = get_base_color(candy_type)
        for r in range(GRID_SIZE):
            if board[r][col] != -1:
                affected_cells.append((r, col))
                # Add animation
                animations.append(Animation('match', (r, col), duration=0.5, 
                                           color=CANDY_COLORS[base_color]))
                
    elif WRAPPED_START <= candy_type < COLOR_BOMB:
        # Activate wrapped candy - clear 3x3 area
        base_color = get_base_color(candy_type)
        for r in range(max(0, row-1), min(GRID_SIZE, row+2)):
            for c in range(max(0, col-1), min(GRID_SIZE, col+2)):
                if board[r][c] != -1:
                    affected_cells.append((r, c))
                    # Add animation
                    animations.append(Animation('match', (r, c), duration=0.5, 
                                               color=CANDY_COLORS[base_color]))
                    
    elif candy_type == COLOR_BOMB:
        # Get a random color to clear
        colors_on_board = set()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] != -1 and board[r][c] != COLOR_BOMB:
                    colors_on_board.add(get_base_color(board[r][c]))
        
        if colors_on_board:
            color_to_clear = random.choice(list(colors_on_board))
            # Clear all candies of that color
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if get_base_color(board[r][c]) == color_to_clear:
                        affected_cells.append((r, c))
                        # Add animation
                        animations.append(Animation('match', (r, c), duration=0.5, 
                                                   color=CANDY_COLORS[color_to_clear]))
    
    # Play sound
    SPECIAL_SOUND.play()
    
    # Clear all affected cells
    for r, c in affected_cells:
        board[r][c] = -1
    
    # Add score based on number of cells cleared
    score += len(affected_cells) * 10
    
    return affected_cells

def handle_special_combination(candy1, candy2):
    """Handle combinations of special candies"""
    global score, animations
    row1, col1 = candy1
    row2, col2 = candy2
    type1 = board[row1][col1]
    type2 = board[row2][col2]
    affected_cells = []
    
    # Play combo sound
    COMBO_SOUND.play()
    
    # Striped + Striped
    if ((STRIPED_HORIZONTAL_START <= type1 < WRAPPED_START and 
         STRIPED_HORIZONTAL_START <= type2 < WRAPPED_START)):
        # Clear entire row and column
        base_color = get_base_color(type1)
        for r in range(GRID_SIZE):
            if board[r][col1] != -1:
                affected_cells.append((r, col1))  # Clear column
                animations.append(Animation('match', (r, col1), duration=0.5, 
                                           color=CANDY_COLORS[base_color]))
        for c in range(GRID_SIZE):
            if board[row1][c] != -1:
                affected_cells.append((row1, c))  # Clear row
                animations.append(Animation('match', (row1, c), duration=0.5, 
                                           color=CANDY_COLORS[base_color]))
            
    # Striped + Wrapped
    elif ((STRIPED_HORIZONTAL_START <= type1 < WRAPPED_START and WRAPPED_START <= type2 < COLOR_BOMB) or
          (STRIPED_HORIZONTAL_START <= type2 < WRAPPED_START and WRAPPED_START <= type1 < COLOR_BOMB)):
        # Clear 3 rows and 3 columns
        base_color = get_base_color(type1) if STRIPED_HORIZONTAL_START <= type1 < WRAPPED_START else get_base_color(type2)
        for r in range(max(0, row1-1), min(GRID_SIZE, row1+2)):
            for c in range(GRID_SIZE):
                if board[r][c] != -1:
                    affected_cells.append((r, c))  # Clear 3 rows
                    animations.append(Animation('match', (r, c), duration=0.5, 
                                               color=CANDY_COLORS[base_color]))
        for c in range(max(0, col1-1), min(GRID_SIZE, col1+2)):
            for r in range(GRID_SIZE):
                if board[r][c] != -1:
                    affected_cells.append((r, c))  # Clear 3 columns
                    animations.append(Animation('match', (r, c), duration=0.5, 
                                               color=CANDY_COLORS[base_color]))
                
    # Striped + Color Bomb
    elif ((STRIPED_HORIZONTAL_START <= type1 < WRAPPED_START and type2 == COLOR_BOMB) or
          (STRIPED_HORIZONTAL_START <= type2 < WRAPPED_START and type1 == COLOR_BOMB)):
        # Get the color of the striped candy
        color = get_base_color(type1) if STRIPED_HORIZONTAL_START <= type1 < WRAPPED_START else get_base_color(type2)
        is_horizontal = (STRIPED_HORIZONTAL_START <= type1 < STRIPED_VERTICAL_START or 
                         STRIPED_HORIZONTAL_START <= type2 < STRIPED_VERTICAL_START)
        
        # Convert all candies of that color to striped and activate them
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if get_base_color(board[r][c]) == color:
                    # Make it striped based on original orientation
                    if is_horizontal:
                        board[r][c] = STRIPED_HORIZONTAL_START + color
                    else:
                        board[r][c] = STRIPED_VERTICAL_START + color
                    # Activate it
                    affected_cells.extend(activate_special_candy(r, c))
                    
    # Wrapped + Wrapped
    elif (WRAPPED_START <= type1 < COLOR_BOMB and WRAPPED_START <= type2 < COLOR_BOMB):
        # Clear a 5x5 area twice (we'll just do a larger area)
        base_color = get_base_color(type1)
        for r in range(max(0, row1-2), min(GRID_SIZE, row1+3)):
            for c in range(max(0, col1-2), min(GRID_SIZE, col1+3)):
                if board[r][c] != -1:
                    affected_cells.append((r, c))
                    animations.append(Animation('match', (r, c), duration=0.5, 
                                               color=CANDY_COLORS[base_color]))
                
    # Wrapped + Color Bomb
    elif ((WRAPPED_START <= type1 < COLOR_BOMB and type2 == COLOR_BOMB) or
          (WRAPPED_START <= type2 < COLOR_BOMB and type1 == COLOR_BOMB)):
        # Get the color of the wrapped candy
        color = get_base_color(type1) if WRAPPED_START <= type1 < COLOR_BOMB else get_base_color(type2)
        
        # Convert all candies of that color to wrapped and activate them
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if get_base_color(board[r][c]) == color:
                    board[r][c] = WRAPPED_START + color
                    affected_cells.extend(activate_special_candy(r, c))
                    
    # Color Bomb + Color Bomb
    elif (type1 == COLOR_BOMB and type2 == COLOR_BOMB):
        # Clear the entire board
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] != -1:
                    affected_cells.append((r, c))
                    animations.append(Animation('match', (r, c), duration=0.5, 
                                               color=(255, 255, 255)))  # White explosion
    
    # Clear all affected cells
    for r, c in affected_cells:
        board[r][c] = -1
    
    # Add score based on number of cells cleared
    score += len(affected_cells) * 20  # Double points for combinations
    
    return len(affected_cells) > 0  # Return True if any cells were affected
def drop_candies(grid):
    """
    Dịch chuyển các viên kẹo phía trên xuống khi có kẹo bị phá vỡ.
    """
    for col in range(GRID_SIZE):
        empty_rows = []  # Danh sách các hàng trống trong cột này
        
        # Tìm các ô trống từ dưới lên
        for row in range(GRID_SIZE - 1, -1, -1):
            if grid[row][col] is None:
                empty_rows.append(row)
            elif empty_rows:
                # Nếu có ô trống phía dưới, di chuyển kẹo xuống
                new_row = empty_rows.pop(0)
                grid[new_row][col] = grid[row][col]
                grid[row][col] = None
                empty_rows.append(row)  # Hàng này giờ trống
        
        # Thêm kẹo mới vào ô trống trên cùng
        for row in empty_rows:
            grid[row][col] = random.choice(CANDY_COLORS)

def remove_matched_candies(grid):
    """
    Loại bỏ các viên kẹo đã khớp và kích hoạt hiệu ứng rơi.
    """
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] == 'matched':  # Giả định kẹo bị phá được đánh dấu 'matched'
                grid[row][col] = None  # Xóa kẹo
    
    # Gọi hàm để kẹo phía trên rơi xuống
    drop_candies(grid)

def resolve_matches():
    """Remove matched candies, create special candies, and update score"""
    global score, animations
    
    matches, match_positions = check_for_matches()
    if not matches:
        return False
    
    # Play match sound
    MATCH_SOUND.play()
    
    # Detect special patterns
    special_candies = detect_special_patterns(matches, match_positions)
    
    # Update score - more candies = higher score multiplier
    match_size = len(match_positions)
    points = match_size * 10
    
    # Bonus points for larger matches
    if match_size >= 4:
        points *= 2  # Double points for 4+ matches
    if match_size >= 5:
        points *= 2  # 4x points for 5+ matches
    
    score += points
    
    # Create special candies first
    for candy_type, row, col in special_candies:
        create_special_candy(candy_type, row, col)
        # Remove this position from match_positions so it doesn't get cleared
        if (row, col) in match_positions:
            match_positions.remove((row, col))
    
    # Add match animations and mark matched positions with -1 (to be filled later)
    for row, col in match_positions:
        candy_type = board[row][col]
        if candy_type != -1:
            color_idx = get_base_color(candy_type)
            if color_idx >= 0 and color_idx < len(CANDY_COLORS):
                animations.append(Animation('match', (row, col), duration=0.5, 
                                           color=CANDY_COLORS[color_idx]))
            board[row][col] = -1  # Đánh dấu vị trí này là rỗng để chuẩn bị cho kẹo rơi xuống
    
    # Gọi hàm để làm kẹo phía trên rơi xuống
    drop_candies(board)

    return True


def fill_board():
    """Fill empty spaces with candies from above, then add new ones at the top"""
    global animations
    
    # Move candies down to fill gaps
    for col in range(GRID_SIZE):
        # Count empty spaces and shift candies down
        empty_count = 0
        for row in range(GRID_SIZE - 1, -1, -1):
            if board[row][col] == -1:
                empty_count += 1
            elif empty_count > 0:
                # Add fall animation
                animations.append(Animation('fall', (row, col), (row + empty_count, col), 0.3))
                
                # Move the candy down
                board[row + empty_count][col] = board[row][col]
                board[row][col] = -1
    
    # Fill the top with new candies
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE):
            if board[row][col] == -1:
                # Add new candy animation (falling from above the board)
                animations.append(Animation('fall', (row - 3, col), (row, col), 0.3))
                
                # Create new candy
                board[row][col] = random.randint(0, len(CANDY_COLORS) - 1)

def find_possible_moves():
    """Find all possible moves that would create a match"""
    possible_moves = []
    
    # Check each position
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            # Skip empty cells
            if board[row][col] == -1:
                continue
                
            # Try swapping with right neighbor
            if col < GRID_SIZE - 1 and board[row][col + 1] != -1:
                # Swap
                swap_candies((row, col), (row, col + 1))
                # Check if this creates a match
                matches, _ = check_for_matches()
                if matches:
                    possible_moves.append((row, col, row, col + 1))
                # Swap back
                swap_candies((row, col), (row, col + 1))
            
            # Try swapping with bottom neighbor
            if row < GRID_SIZE - 1 and board[row + 1][col] != -1:
                # Swap
                swap_candies((row, col), (row + 1, col))
                # Check if this creates a match
                matches, _ = check_for_matches()
                if matches:
                    possible_moves.append((row, col, row + 1, col))
                # Swap back
                swap_candies((row, col), (row + 1, col))
    
    return possible_moves

def show_hint():
    """Show a hint for a possible move"""
    global hint_candy
    
    possible_moves = find_possible_moves()
    if possible_moves:
        # Choose a random move from the possible ones
        hint_candy = random.choice(possible_moves)
    else:
        hint_candy = None
        # If no moves are possible, shuffle the board
        shuffle_board()

def shuffle_board():
    """Shuffle the board when no moves are available"""
    global board, animations
    
    # Add shuffle animation
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] != -1:
                # Random position within the board
                new_row = random.randint(0, GRID_SIZE - 1)
                new_col = random.randint(0, GRID_SIZE - 1)
                animations.append(Animation('swap', (row, col), (new_row, new_col), 0.5))
    
    # Flatten the board
    flat_board = [board[row][col] for row in range(GRID_SIZE) for col in range(GRID_SIZE)]
    # Shuffle
    random.shuffle(flat_board)
    # Rebuild the board
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            board[row][col] = flat_board[row * GRID_SIZE + col]
    
    # Make sure there are no matches after shuffling
    while check_for_matches()[0]:
        resolve_matches()
        fill_board()
    
    # Make sure there are possible moves after shuffling
    if not find_possible_moves():
        shuffle_board()  # Recursively shuffle until we have valid moves

def check_game_over():
    """Check if the game is over (win or lose)"""
    global game_state, total_score, current_level
    
    if score >= target_score:
        # Level complete
        LEVEL_COMPLETE_SOUND.play()
        total_score += score
        game_state = LEVEL_COMPLETE
    elif moves_left <= 0:
        # Game over
        GAME_OVER_SOUND.play()
        total_score += score
        game_state = GAME_OVER

def next_level():
    """Advance to the next level"""
    global current_level, game_state
    
    current_level += 1
    if current_level > len(level_config):
        # Player beat all levels, go back to level 1 with higher difficulty
        current_level = 1
    
    initialize_board()
    game_state = PLAYING

def main():
    global selected_candy, game_state, hint_candy, last_action_time, moves_left, animations
    
    initialize_board()
    game_state = MENU
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == MOUSEBUTTONDOWN:
                # Handle button clicks
                if game_state == MENU:
                    if buttons['play'].is_clicked(mouse_pos):
                        initialize_board()
                        game_state = PLAYING
                
                elif game_state == PLAYING:
                    # Check if any game buttons were clicked
                    if buttons['pause'].is_clicked(mouse_pos):
                        game_state = PAUSED
                    elif buttons['hint'].is_clicked(mouse_pos):
                        show_hint()
                    elif buttons['shuffle'].is_clicked(mouse_pos):
                        if not find_possible_moves():
                            shuffle_board()
                    else:
                        # Handle candy selection
                        mouse_x, mouse_y = event.pos
                        clicked_candy = get_candy_at_pixel(mouse_x, mouse_y)
                        
                        if clicked_candy:
                            if selected_candy is None:
                                selected_candy = clicked_candy
                                last_action_time = time.time()
                            else:
                                # If the clicked candy is adjacent to the selected one, swap them
                                if are_adjacent(selected_candy, clicked_candy):
                                    # Check if both candies are special
                                    row1, col1 = selected_candy
                                    row2, col2 = clicked_candy
                                    
                                    # Special candy combination
                                    if ((board[row1][col1] >= STRIPED_HORIZONTAL_START or 
                                         board[row1][col1] == COLOR_BOMB) and 
                                        (board[row2][col2] >= STRIPED_HORIZONTAL_START or 
                                         board[row2][col2] == COLOR_BOMB)):
                                        
                                        swap_candies(selected_candy, clicked_candy)
                                        handle_special_combination(selected_candy, clicked_candy)
                                        moves_left -= 1
                                        last_action_time = time.time()
                                        hint_candy = None
                                        
                                        # Fill board after special combination
                                        fill_board()
                                        
                                        # Check if there are no more moves
                                        if not find_possible_moves():
                                            shuffle_board()
                                        
                                        # Check if game is over
                                        check_game_over()
                                    else:
                                        # Regular candy swap
                                        swap_candies(selected_candy, clicked_candy)
                                        
                                        # Check if the swap created any matches
                                        if not resolve_matches():
                                            # If no matches, swap back
                                            swap_candies(selected_candy, clicked_candy)
                                        else:
                                            # Use a move
                                            moves_left -= 1
                                            last_action_time = time.time()
                                            hint_candy = None
                                            
                                            # Continue resolving matches until no more are found
                                            while True:
                                                # Wait for animations to complete
                                                waiting_for_animations = True
                                                while waiting_for_animations:
                                                    waiting_for_animations = False
                                                    for anim in animations:
                                                        if not anim.completed:
                                                            anim.update()
                                                            waiting_for_animations = True
                                                    if waiting_for_animations:
                                                        pygame.time.wait(10)
                                                
                                                fill_board()
                                                if not resolve_matches():
                                                    break
                                            
                                            # Check if there are no more moves
                                            if not find_possible_moves():
                                                shuffle_board()
                                            
                                            # Check if game is over
                                            check_game_over()
                                
                                selected_candy = None
                
                elif game_state == PAUSED:
                    if buttons['resume'].is_clicked(mouse_pos):
                        game_state = PLAYING
                    elif buttons['restart'].is_clicked(mouse_pos):
                        initialize_board()
                        game_state = PLAYING
                    elif buttons['quit'].is_clicked(mouse_pos):
                        game_state = MENU
                
                elif game_state == LEVEL_COMPLETE:
                    if buttons['next_level'].is_clicked(mouse_pos):
                        next_level()
                    elif buttons['menu'].is_clicked(mouse_pos):
                        game_state = MENU
                
                elif game_state == GAME_OVER:
                    if buttons['try_again'].is_clicked(mouse_pos):
                        initialize_board()
                        game_state = PLAYING
                    elif buttons['menu'].is_clicked(mouse_pos):
                        game_state = MENU
        
        # Update animations
        for anim in animations[:]:
            if anim.update():
                animations.remove(anim)
        
        # Draw the current game state
        draw_board()
        
        # Check for hint timer
        if game_state == PLAYING and hint_candy is None:
            current_time = time.time()
            if current_time - last_action_time > 5:  # Show hint after 5 seconds of inactivity
                show_hint()
        
        pygame.display.update()
        CLOCK.tick(FPS)

if __name__ == '__main__':
    main()

print("Code executed successfully. Run this file to play the Candy Crush game with special candies!")