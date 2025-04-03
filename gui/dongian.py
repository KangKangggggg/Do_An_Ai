import pygame
import random
import sys
import time
from pygame.locals import *

# Initialize pygame
pygame.init()

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

# Set up the window
DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Candy Crush Clone')
CLOCK = pygame.time.Clock()

# Game variables
board = []
selected_candy = None
score = 0
target_score = 1000  # Target score to complete the level
moves_left = 20      # Number of moves allowed
game_state = MENU
hint_timer = 0
hint_candy = None
last_action_time = 0

# Fonts
title_font = pygame.font.SysFont('Arial', 48, bold=True)
button_font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)

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
    
    return buttons

buttons = create_buttons()

def initialize_board():
    """Create a new game board filled with random candies"""
    global board, score, moves_left, game_state, hint_candy, last_action_time
    
    board = []
    for _ in range(GRID_SIZE):
        row = []
        for _ in range(GRID_SIZE):
            row.append(random.randint(0, len(CANDY_COLORS) - 1))
        board.append(row)
    
    # Check for matches at the start and resolve them
    while check_for_matches():
        resolve_matches()
        fill_board()
    
    # Reset game variables
    score = 0
    moves_left = 20
    hint_candy = None
    last_action_time = time.time()
    game_state = PLAYING

def draw_board():
    """Draw the game board and candies"""
    DISPLAY_SURF.fill(WHITE)
    
    # Draw grid lines
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(DISPLAY_SURF, BLACK, (x, 0), (x, GAME_AREA_HEIGHT), 1)
    for y in range(0, GAME_AREA_HEIGHT, CELL_SIZE):
        pygame.draw.line(DISPLAY_SURF, BLACK, (0, y), (WINDOW_WIDTH, y), 1)
    
    # Draw candies
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            candy_color = CANDY_COLORS[board[row][col]]
            pygame.draw.circle(
                DISPLAY_SURF, 
                candy_color, 
                (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), 
                CELL_SIZE // 2 - 5
            )
    
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
    
    elif game_state == MENU:
        # Draw title
        title_text = title_font.render("Candy Crush", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        DISPLAY_SURF.blit(title_text, title_rect)
        
        # Draw play button
        buttons['play'].update(mouse_pos)
        buttons['play'].draw()
    
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
    row1, col1 = candy1
    row2, col2 = candy2
    
    board[row1][col1], board[row2][col2] = board[row2][col2], board[row1][col1]

def are_adjacent(candy1, candy2):
    """Check if two candies are adjacent"""
    row1, col1 = candy1
    row2, col2 = candy2
    
    return (abs(row1 - row2) == 1 and col1 == col2) or (abs(col1 - col2) == 1 and row1 == row2)

def check_for_matches():
    """Check for matches of 3 or more candies in a row or column"""
    matches = []
    
    # Check horizontal matches
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 2):
            if board[row][col] == board[row][col + 1] == board[row][col + 2]:
                # Find how long this match is
                match_length = 3
                while col + match_length < GRID_SIZE and board[row][col] == board[row][col + match_length]:
                    match_length += 1
                
                # Add all positions in this match
                match = []
                for i in range(match_length):
                    match.append((row, col + i))
                matches.append(match)
    
    # Check vertical matches
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE - 2):
            if board[row][col] == board[row + 1][col] == board[row + 2][col]:
                # Find how long this match is
                match_length = 3
                while row + match_length < GRID_SIZE and board[row][col] == board[row + match_length][col]:
                    match_length += 1
                
                # Add all positions in this match
                match = []
                for i in range(match_length):
                    match.append((row + i, col))
                matches.append(match)
    
    return matches

def resolve_matches():
    """Remove matched candies and update score"""
    global score
    
    matches = check_for_matches()
    if not matches:
        return False
    
    # Flatten the list of matches and remove duplicates
    all_matched = set()
    for match in matches:
        for pos in match:
            all_matched.add(pos)
    
    # Update score - more candies = higher score multiplier
    match_size = len(all_matched)
    points = match_size * 10
    
    # Bonus points for larger matches
    if match_size >= 4:
        points *= 2  # Double points for 4+ matches
    if match_size >= 5:
        points *= 2  # 4x points for 5+ matches
    
    score += points
    
    # Mark matched positions with -1 (to be filled later)
    for row, col in all_matched:
        board[row][col] = -1
    
    return True

def fill_board():
    """Fill empty spaces with candies from above, then add new ones at the top"""
    # Move candies down to fill gaps
    for col in range(GRID_SIZE):
        # Count empty spaces and shift candies down
        empty_count = 0
        for row in range(GRID_SIZE - 1, -1, -1):
            if board[row][col] == -1:
                empty_count += 1
            elif empty_count > 0:
                board[row + empty_count][col] = board[row][col]
                board[row][col] = -1
    
    # Fill the top with new candies
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE):
            if board[row][col] == -1:
                board[row][col] = random.randint(0, len(CANDY_COLORS) - 1)

def find_possible_moves():
    """Find all possible moves that would create a match"""
    possible_moves = []
    
    # Check each position
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            # Try swapping with right neighbor
            if col < GRID_SIZE - 1:
                # Swap
                swap_candies((row, col), (row, col + 1))
                # Check if this creates a match
                if check_for_matches():
                    possible_moves.append((row, col, row, col + 1))
                # Swap back
                swap_candies((row, col), (row, col + 1))
            
            # Try swapping with bottom neighbor
            if row < GRID_SIZE - 1:
                # Swap
                swap_candies((row, col), (row + 1, col))
                # Check if this creates a match
                if check_for_matches():
                    possible_moves.append((row, col, row + 1, col))
                # Swap back
                swap_candies((row, col), (row + 1, col))
    
    return possible_moves

def shuffle_board():
    """Shuffle the board when no moves are available"""
    global board
    
    # Flatten the board
    flat_board = [board[row][col] for row in range(GRID_SIZE) for col in range(GRID_SIZE)]
    # Shuffle
    random.shuffle(flat_board)
    # Rebuild the board
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            board[row][col] = flat_board[row * GRID_SIZE + col]
    
    # Make sure there are no matches after shuffling
    while check_for_matches():
        resolve_matches()
        fill_board()
    
    # Make sure there are possible moves after shuffling
    if not find_possible_moves():
        shuffle_board()  # Recursively shuffle until we have valid moves

def show_hint():
    """Show a hint for a possible move"""
    global hint_candy
    
    possible_moves = find_possible_moves()
    if possible_moves:
        # Choose a random move from the possible ones
        hint_candy = random.choice(possible_moves)
    else:
        hint_candy = None

def check_game_over():
    """Check if the game is over (win or lose)"""
    global game_state
    
    if score >= target_score:
        show_message("Level Complete!", f"Score: {score}", "Click to continue")
        initialize_board()
    elif moves_left <= 0:
        show_message("Game Over", f"Score: {score}", "Click to restart")
        initialize_board()

def show_message(title, message, action_text):
    """Show a message box with a title, message, and action text"""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 192))
    DISPLAY_SURF.blit(overlay, (0, 0))
    
    # Draw message box
    message_box = pygame.Rect(WINDOW_WIDTH//4, WINDOW_HEIGHT//4, WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
    pygame.draw.rect(DISPLAY_SURF, WHITE, message_box)
    pygame.draw.rect(DISPLAY_SURF, BLACK, message_box, 3)
    
    # Draw title
    title_text = title_font.render(title, True, BLACK)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
    DISPLAY_SURF.blit(title_text, title_rect)
    
    # Draw message
    message_text = button_font.render(message, True, BLACK)
    message_rect = message_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    DISPLAY_SURF.blit(message_text, message_rect)
    
    # Draw action text
    action_text = small_font.render(action_text, True, DARK_GRAY)
    action_rect = action_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*2//3))
    DISPLAY_SURF.blit(action_text, action_rect)
    
    pygame.display.update()
    
    # Wait for click
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                waiting = False

def main():
    global selected_candy, game_state, hint_candy, last_action_time, moves_left
    
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