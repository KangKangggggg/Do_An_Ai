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
SLIME_COLOR = (180, 180, 255, 150)  # Semi-transparent overlay

# Special candy markers
STRIPED_CANDY_HORIZONTAL = 10   # Kẹo sọc ngang
BOMB_CANDY = 11                 # Bomb candy (sẽ hiển thị đa màu)
WRAPPED_CANDY = 12              # Wrapped candy (kẹo bịch)
STRIPED_CANDY_VERTICAL = 13     # Kẹo sọc dọc

# Set up the window
DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Candy Crush Clone')
CLOCK = pygame.time.Clock()

# Game variables
board = []
# Mảng slime: True nếu ô đó có chất nhờn, False nếu không
slime_board = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
selected_candy = None
score = 0
target_score = 1000  # Target score to complete the level
moves_left = 20      # Number of moves allowed
game_state = MENU
hint_timer = 0
hint_candy = None
last_action_time = 0

# EXP variables
exp = 0
exp_needed = 500  # EXP cần đạt để qua màn

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
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(DISPLAY_SURF, color, self.rect)
        pygame.draw.rect(DISPLAY_SURF, BLACK, self.rect, 2)
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
    buttons['play'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, 200, 50, "▶️ Play")
    button_width = WINDOW_WIDTH // 7
    buttons['score'] = Button(0, GAME_AREA_HEIGHT, button_width, BUTTON_HEIGHT, "🎯 Score")
    buttons['moves'] = Button(button_width, GAME_AREA_HEIGHT, button_width, BUTTON_HEIGHT, "🔢 Moves")
    buttons['goal'] = Button(button_width*2, GAME_AREA_HEIGHT, button_width, BUTTON_HEIGHT, "🎯 Goal")
    buttons['hint'] = Button(button_width*3, GAME_AREA_HEIGHT, button_width, BUTTON_HEIGHT, "💡 Hint")
    buttons['shuffle'] = Button(button_width*4, GAME_AREA_HEIGHT, button_width, BUTTON_HEIGHT, "🔄 Shuffle")
    buttons['pause'] = Button(button_width*5, GAME_AREA_HEIGHT, button_width*2, BUTTON_HEIGHT, "⏸️ Pause")
    buttons['resume'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 60, 200, 50, "▶️ Resume")
    buttons['restart'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, 200, 50, "🔄 Restart")
    buttons['quit'] = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 60, 200, 50, "❌ Quit")
    return buttons

buttons = create_buttons()

def initialize_board():
    """Create a new game board filled with random candies and initialize slime."""
    global board, slime_board, score, moves_left, game_state, hint_candy, last_action_time, exp
    board = []
    for _ in range(GRID_SIZE):
        row = []
        for _ in range(GRID_SIZE):
            row.append(random.randint(0, len(CANDY_COLORS) - 1))
        board.append(row)
    # Khởi tạo slime: ví dụ, 20% ô ngẫu nhiên chứa slime
    slime_board = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    num_slime = (GRID_SIZE * GRID_SIZE) // 5
    count = 0
    while count < num_slime:
        r = random.randint(0, GRID_SIZE - 1)
        c = random.randint(0, GRID_SIZE - 1)
        if not slime_board[r][c]:
            slime_board[r][c] = True
            count += 1

    # Kiểm tra và xử lý các match ban đầu
    while check_for_matches():
        resolve_matches()
        fill_board()
    
    score = 0
    moves_left = 20
    exp = 0
    hint_candy = None
    last_action_time = time.time()
    game_state = PLAYING

def detect_L_shapes():
    """
    Quét bảng và trả về danh sách các L-shape combo.
    Mỗi phần tử là tuple (intersection, cells) với:
      - intersection: vị trí giao nhau (sẽ trở thành Wrapped Candy).
      - cells: danh sách các ô trong combo L-shape.
    Combo L-shape được xác định khi có 3 viên theo hàng và 3 viên theo cột chia sẻ 1 ô chung.
    """
    l_shapes = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            current = board[i][j]
            if current >= len(CANDY_COLORS):
                continue
            # Right-Down
            if i + 2 < GRID_SIZE and j + 2 < GRID_SIZE:
                if board[i][j+1] == current and board[i][j+2] == current and \
                   board[i+1][j] == current and board[i+2][j] == current:
                    cells = {(i, j), (i, j+1), (i, j+2), (i+1, j), (i+2, j)}
                    l_shapes.append(((i, j), list(cells)))
            # Left-Down
            if i + 2 < GRID_SIZE and j - 2 >= 0:
                if board[i][j-1] == current and board[i][j-2] == current and \
                   board[i+1][j] == current and board[i+2][j] == current:
                    cells = {(i, j), (i, j-1), (i, j-2), (i+1, j), (i+2, j)}
                    l_shapes.append(((i, j), list(cells)))
            # Right-Up
            if i - 2 >= 0 and j + 2 < GRID_SIZE:
                if board[i][j+1] == current and board[i][j+2] == current and \
                   board[i-1][j] == current and board[i-2][j] == current:
                    cells = {(i, j), (i, j+1), (i, j+2), (i-1, j), (i-2, j)}
                    l_shapes.append(((i, j), list(cells)))
            # Left-Up
            if i - 2 >= 0 and j - 2 >= 0:
                if board[i][j-1] == current and board[i][j-2] == current and \
                   board[i-1][j] == current and board[i-2][j] == current:
                    cells = {(i, j), (i, j-1), (i, j-2), (i-1, j), (i-2, j)}
                    l_shapes.append(((i, j), list(cells)))
    return l_shapes

def resolve_matches():
    """
    Xử lý match: phá các candy, loại bỏ slime nếu có, cập nhật EXP & điểm.
    - Match 3: +10 EXP.
    - Match 4: +20 EXP và tạo ra Striped Candy (với hướng ngẫu nhiên).
    - Match >=5: +20 EXP và tạo ra Bomb Candy.
    - Combo L-shape: +30 EXP và tạo Wrapped Candy.
    Nếu ô match có chứa slime, loại bỏ slime và cộng thêm 20 EXP.
    """
    global score, exp
    # Xử lý combo L-shape
    l_shapes = detect_L_shapes()
    for (intersection, cells) in l_shapes:
        exp += 30
        r, c = intersection
        board[r][c] = WRAPPED_CANDY
        for cell in cells:
            if cell != intersection:
                board[cell[0]][cell[1]] = -1

    matches = check_for_matches()
    if not matches and not l_shapes:
        return False
    all_matched = set()
    for match in matches:
        all_matched.update(match)
        match_length = len(match)
        if match_length == 3:
            exp += 10
        elif match_length == 4:
            exp += 20
            orientation = random.choice([STRIPED_CANDY_HORIZONTAL, STRIPED_CANDY_VERTICAL])
            r, c = match[0]
            board[r][c] = orientation
            all_matched.remove((r, c))
        elif match_length >= 5:
            exp += 20
            r, c = match[0]
            board[r][c] = BOMB_CANDY
            all_matched.remove((r, c))
    for (r, c) in list(all_matched):
        if slime_board[r][c]:
            slime_board[r][c] = False
            exp += 20
    score += len(all_matched) * 10
    for (r, c) in all_matched:
        board[r][c] = -1
    return True

def fill_board():
    """Đổ lại bảng sau khi match."""
    for col in range(GRID_SIZE):
        empty_count = 0
        for row in range(GRID_SIZE - 1, -1, -1):
            if board[row][col] == -1:
                empty_count += 1
            elif empty_count > 0:
                board[row + empty_count][col] = board[row][col]
                board[row][col] = -1
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE):
            if board[row][col] == -1:
                board[row][col] = random.randint(0, len(CANDY_COLORS) - 1)

def check_for_matches():
    """Tìm các hàng/cột có 3+ viên cùng loại (chỉ với candy thông thường)."""
    matches = []
    for row in range(GRID_SIZE):
        col = 0
        while col < GRID_SIZE - 2:
            current = board[row][col]
            if current < len(CANDY_COLORS):
                match = [(row, col)]
                j = col + 1
                while j < GRID_SIZE and board[row][j] == current:
                    match.append((row, j))
                    j += 1
                if len(match) >= 3:
                    matches.append(match)
                col = j
            else:
                col += 1
    for col in range(GRID_SIZE):
        row = 0
        while row < GRID_SIZE - 2:
            current = board[row][col]
            if current < len(CANDY_COLORS):
                match = [(row, col)]
                i = row + 1
                while i < GRID_SIZE and board[i][col] == current:
                    match.append((i, col))
                    i += 1
                if len(match) >= 3:
                    matches.append(match)
                row = i
            else:
                row += 1
    return matches

def swap_candies(candy1, candy2):
    """Chỉ cho phép swap nếu cả 2 ô không bị slime."""
    row1, col1 = candy1
    row2, col2 = candy2
    if slime_board[row1][col1] or slime_board[row2][col2]:
        return
    board[row1][col1], board[row2][col2] = board[row2][col2], board[row1][col1]

def are_adjacent(candy1, candy2):
    row1, col1 = candy1
    row2, col2 = candy2
    return (abs(row1 - row2) == 1 and col1 == col2) or (abs(col1 - col2) == 1 and row1 == row2)

def find_possible_moves():
    possible_moves = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if col < GRID_SIZE - 1:
                swap_candies((row, col), (row, col + 1))
                if check_for_matches():
                    possible_moves.append((row, col, row, col + 1))
                swap_candies((row, col), (row, col + 1))
            if row < GRID_SIZE - 1:
                swap_candies((row, col), (row + 1, col))
                if check_for_matches():
                    possible_moves.append((row, col, row + 1, col))
                swap_candies((row, col), (row + 1, col))
    return possible_moves

def shuffle_board():
    global board
    flat_board = [board[row][col] for row in range(GRID_SIZE) for col in range(GRID_SIZE)]
    random.shuffle(flat_board)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            board[row][col] = flat_board[row * GRID_SIZE + col]
    while check_for_matches():
        resolve_matches()
        fill_board()
    if not find_possible_moves():
        shuffle_board()

def show_hint():
    global hint_candy
    possible_moves = find_possible_moves()
    if possible_moves:
        hint_candy = random.choice(possible_moves)
    else:
        hint_candy = None

def check_game_over():
    """
    Nếu tất cả các ô có slime bị phá (remaining_slime == 0) trước khi hết 20 bước, thắng.
    Nếu moves_left hết mà vẫn còn slime, game over.
    """
    global game_state
    remaining_slime = sum(1 for row in slime_board for cell in row if cell)
    if remaining_slime == 0:
        show_message("Level Complete!", f"Score: {score} EXP: {exp}", "Click to continue")
        initialize_board()
    elif moves_left <= 0:
        show_message("Game Over", f"Score: {score} EXP: {exp}", "Click to restart")
        initialize_board()

def activate_striped_candy(pos, orientation):
    """Khi được kích hoạt, nếu orientation là STRIPED_CANDY_HORIZONTAL thì phá hủy hàng ngang,
       nếu STRIPED_CANDY_VERTICAL thì phá hủy cột dọc tại vị trí đó."""
    row, col = pos
    if orientation == STRIPED_CANDY_HORIZONTAL:
        for j in range(GRID_SIZE):
            board[row][j] = -1
    elif orientation == STRIPED_CANDY_VERTICAL:
        for i in range(GRID_SIZE):
            board[i][col] = -1
    fill_board()

def activate_bomb_candy(pos, target_color):
    """Khi được kích hoạt, phá hủy tất cả các viên kẹo cùng màu với target_color."""
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if board[i][j] == target_color:
                board[i][j] = -1
    fill_board()

def activate_wrapped_candy(pos):
    """Wrapped candy phá hủy 1 hàng và 1 cột tại vị trí nó đứng."""
    row, col = pos
    for j in range(GRID_SIZE):
        board[row][j] = -1
    for i in range(GRID_SIZE):
        board[i][col] = -1
    fill_board()

def draw_board():
    """Draw the game board, candies and overlay slime. Vẽ thêm các special candy."""
    DISPLAY_SURF.fill(WHITE)
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(DISPLAY_SURF, BLACK, (x, 0), (x, GAME_AREA_HEIGHT), 1)
    for y in range(0, GAME_AREA_HEIGHT, CELL_SIZE):
        pygame.draw.line(DISPLAY_SURF, BLACK, (0, y), (WINDOW_WIDTH, y), 1)
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            candy_val = board[row][col]
            if candy_val < len(CANDY_COLORS):
                candy_color = CANDY_COLORS[candy_val]
            elif candy_val == STRIPED_CANDY_HORIZONTAL:
                candy_color = (255, 165, 0)  # Sọc ngang (màu cam)
            elif candy_val == STRIPED_CANDY_VERTICAL:
                candy_color = (255, 165, 0)  # Sọc dọc (màu cam)
            elif candy_val == BOMB_CANDY:
                # Vẽ bomb candy đa màu: vẽ nhiều vòng tròn nhỏ với màu sắc từ CANDY_COLORS
                center = (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)
                radius = CELL_SIZE // 2 - 5
                for i, color in enumerate(CANDY_COLORS):
                    pygame.draw.circle(DISPLAY_SURF, color, center, max(radius - i*2, 2))
                continue  # bỏ qua vẽ vòng tròn mặc định
            elif candy_val == WRAPPED_CANDY:
                candy_color = (0, 128, 128)  # Màu xanh lam đậm
            else:
                candy_color = BLACK

            pygame.draw.circle(
                DISPLAY_SURF, 
                candy_color, 
                (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), 
                CELL_SIZE // 2 - 5
            )
    slime_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    slime_overlay.fill(SLIME_COLOR)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if slime_board[row][col]:
                DISPLAY_SURF.blit(slime_overlay, (col * CELL_SIZE, row * CELL_SIZE))
    
    if selected_candy:
        row, col = selected_candy
        pygame.draw.rect(DISPLAY_SURF, (255, 255, 255), (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
    
    if hint_candy and time.time() % 1 > 0.5:
        row1, col1, row2, col2 = hint_candy
        pygame.draw.rect(DISPLAY_SURF, (255, 255, 0), (col1 * CELL_SIZE, row1 * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        pygame.draw.rect(DISPLAY_SURF, (255, 255, 0), (col2 * CELL_SIZE, row2 * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
    
    mouse_pos = pygame.mouse.get_pos()
    if game_state == PLAYING:
        buttons['score'].text = f"🎯 {score} EXP:{exp}"
        buttons['moves'].text = f"🔢 {moves_left}"
        remaining_slime = sum(1 for row in slime_board for cell in row if cell)
        buttons['goal'].text = f"🧪 Slime: {remaining_slime}"
        for button_name in ['score', 'moves', 'goal', 'hint', 'shuffle', 'pause']:
            buttons[button_name].update(mouse_pos)
            buttons[button_name].draw()
    elif game_state == MENU:
        title_text = title_font.render("Candy Crush", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        DISPLAY_SURF.blit(title_text, title_rect)
        buttons['play'].update(mouse_pos)
        buttons['play'].draw()
    elif game_state == PAUSED:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        DISPLAY_SURF.blit(overlay, (0, 0))
        pause_text = title_font.render("Game Paused", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        DISPLAY_SURF.blit(pause_text, pause_rect)
        for button_name in ['resume', 'restart', 'quit']:
            buttons[button_name].update(mouse_pos)
            buttons[button_name].draw()

def get_candy_at_pixel(x, y):
    if y >= GAME_AREA_HEIGHT:
        return None
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE:
        return None
    return (row, col)

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
                if game_state == MENU:
                    if buttons['play'].is_clicked(mouse_pos):
                        initialize_board()
                        game_state = PLAYING
                elif game_state == PLAYING:
                    if buttons['pause'].is_clicked(mouse_pos):
                        game_state = PAUSED
                    elif buttons['hint'].is_clicked(mouse_pos):
                        show_hint()
                    elif buttons['shuffle'].is_clicked(mouse_pos):
                        if not find_possible_moves():
                            shuffle_board()
                    else:
                        mouse_x, mouse_y = event.pos
                        clicked_candy = get_candy_at_pixel(mouse_x, mouse_y)
                        if clicked_candy:
                            if selected_candy is None:
                                selected_candy = clicked_candy
                                last_action_time = time.time()
                            else:
                                if are_adjacent(selected_candy, clicked_candy):
                                    val1 = board[selected_candy[0]][selected_candy[1]]
                                    val2 = board[clicked_candy[0]][clicked_candy[1]]
                                    if val1 in (STRIPED_CANDY_HORIZONTAL, STRIPED_CANDY_VERTICAL) or val2 in (STRIPED_CANDY_HORIZONTAL, STRIPED_CANDY_VERTICAL):
                                        orientation = val1 if val1 in (STRIPED_CANDY_HORIZONTAL, STRIPED_CANDY_VERTICAL) else val2
                                        target_pos = clicked_candy if val1 in (STRIPED_CANDY_HORIZONTAL, STRIPED_CANDY_VERTICAL) else selected_candy
                                        activate_striped_candy(target_pos, orientation)
                                    elif val1 == BOMB_CANDY or val2 == BOMB_CANDY:
                                        target_color = None
                                        if val1 == BOMB_CANDY and val2 < len(CANDY_COLORS):
                                            target_color = board[clicked_candy[0]][clicked_candy[1]]
                                        elif val2 == BOMB_CANDY and val1 < len(CANDY_COLORS):
                                            target_color = board[selected_candy[0]][selected_candy[1]]
                                        if target_color is None:
                                            target_color = random.randint(0, len(CANDY_COLORS)-1)
                                        activate_bomb_candy(selected_candy, target_color)
                                    elif val1 == WRAPPED_CANDY or val2 == WRAPPED_CANDY:
                                        activate_wrapped_candy(selected_candy)
                                    else:
                                        swap_candies(selected_candy, clicked_candy)
                                        if not resolve_matches():
                                            swap_candies(selected_candy, clicked_candy)
                                    moves_left -= 1
                                    last_action_time = time.time()
                                    hint_candy = None
                                    while True:
                                        fill_board()
                                        if not resolve_matches():
                                            break
                                    if not find_possible_moves():
                                        shuffle_board()
                                    check_game_over()
                                    selected_candy = None
                                else:
                                    selected_candy = clicked_candy
                                    last_action_time = time.time()
                elif game_state == PAUSED:
                    if buttons['resume'].is_clicked(mouse_pos):
                        game_state = PLAYING
                    elif buttons['restart'].is_clicked(mouse_pos):
                        initialize_board()
                        game_state = PLAYING
                    elif buttons['quit'].is_clicked(mouse_pos):
                        game_state = MENU
        draw_board()
        if game_state == PLAYING and hint_candy is None:
            current_time = time.time()
            if current_time - last_action_time > 5:
                show_hint()
        pygame.display.update()
        CLOCK.tick(FPS)

if __name__ == '__main__':
    main()