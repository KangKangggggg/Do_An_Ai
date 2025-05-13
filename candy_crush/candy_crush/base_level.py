import pygame
import random
from enum import Enum

# Constants
GRID_SIZE = 9
SQUARE_SIZE = 60
WIDTH = GRID_SIZE * SQUARE_SIZE
HEIGHT = GRID_SIZE * SQUARE_SIZE + 100  # Add space for the score
BG_COLOR = (135, 206, 235)  # Light blue
GRID_COLOR = (100, 149, 237)  # Cornflower blue
SCORE_AREA_HEIGHT = 100
FONT_COLOR = (255, 255, 255)  # White

# Candy Types
class CandyType(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    PURPLE = 4
    ORANGE = 5

# Special Candy Types
class SpecialType(Enum):
    NONE = 0
    STRIPED_HORIZONTAL = 1
    STRIPED_VERTICAL = 2
    WRAPPED = 3
    CHOCOLATE = 4
    INGREDIENT = 5
    STRIPED_H = 6
    STRIPED_V = 7
    COLOR_BOMB = 8

# Blocker Types
class BlockerType(Enum):
    NONE = 0
    SINGLE = 1
    DOUBLE = 2

class Candy:
    def __init__(self, candy_type, special_type=SpecialType.NONE, blocker_type=BlockerType.NONE):
        self.candy_type = candy_type
        self.special_type = special_type
        self.blocker_type = blocker_type
        self.remove = False
        self.ingredient = False
        self.chocolate = False
        self.x = 0
        self.y = 0

    def __repr__(self):
         return f"Candy({self.candy_type}, {self.special_type}, {self.blocker_type})"

    def draw(self, screen, x, y, images):
        self.x = x
        self.y = y
        if self.blocker_type != BlockerType.NONE:
            if self.blocker_type == BlockerType.SINGLE:
                screen.blit(images['blocker_single'], (x, y))
            elif self.blocker_type == BlockerType.DOUBLE:
                screen.blit(images['blocker_double'], (x, y))
        elif self.ingredient:
            screen.blit(images['ingredient'], (x, y))
        elif self.chocolate:
            screen.blit(images['chocolate'], (x, y))
        else:
            screen.blit(images[self.candy_type.name.lower()], (x, y))

class BaseLevel:
    def __init__(self, grid_size=GRID_SIZE):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Candy Crush")
        self.grid_size = grid_size
        self.grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.images = self.load_images()
        self.initialize_grid()

    def load_images(self):
        images = {}
        for candy_type in CandyType:
            images[candy_type.name.lower()] = pygame.image.load(f"assets/{candy_type.name.lower()}.png")
            images[candy_type.name.lower()] = pygame.transform.scale(images[candy_type.name.lower()], (SQUARE_SIZE, SQUARE_SIZE))
        images['blocker_single'] = pygame.image.load("assets/blocker_single.png")
        images['blocker_single'] = pygame.transform.scale(images['blocker_single'], (SQUARE_SIZE, SQUARE_SIZE))
        images['blocker_double'] = pygame.image.load("assets/blocker_double.png")
        images['blocker_double'] = pygame.transform.scale(images['blocker_double'], (SQUARE_SIZE, SQUARE_SIZE))
        images['ingredient'] = pygame.image.load("assets/ingredient.png")
        images['ingredient'] = pygame.transform.scale(images['ingredient'], (SQUARE_SIZE, SQUARE_SIZE))
        images['chocolate'] = pygame.image.load("assets/chocolate.png")
        images['chocolate'] = pygame.transform.scale(images['chocolate'], (SQUARE_SIZE, SQUARE_SIZE))
        return images

    def initialize_grid(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col] = self.create_random_candy()

        # Ensure no initial matches
        while self.find_matches():
            self.remove_matches()
            self.move_candies_down()
            self.fill_empty_spaces()

    def create_random_candy(self):
        candy_type = random.choice(list(CandyType))
        return Candy(candy_type)

    def draw_grid(self):
        self.screen.fill(BG_COLOR)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE
                if self.grid[row][col] is not None:
                    self.grid[row][col].draw(self.screen, x, y, self.images)
                else:
                    pygame.draw.rect(self.screen, GRID_COLOR, (x, y, SQUARE_SIZE, SQUARE_SIZE), 1) # Draw empty grid

    def draw_score(self):
        pygame.draw.rect(self.screen, (0, 0, 0), (0, GRID_SIZE * SQUARE_SIZE, WIDTH, SCORE_AREA_HEIGHT))
        text = self.font.render(f"Score: {self.score}", True, FONT_COLOR)
        text_rect = text.get_rect(center=(WIDTH // 2, GRID_SIZE * SQUARE_SIZE + SCORE_AREA_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def handle_click(self, row, col):
        print(f"Clicked on row: {row}, col: {col}")

    def swap_candies(self, row1, col1, row2, col2):
        self.grid[row1][col1], self.grid[row2][col2] = self.grid[row2][col2], self.grid[row1][col1]

    def undo_swap(self, row1, col1, row2, col2):
        self.swap_candies(row1, col1, row2, col2)

    def is_valid_move(self, row1, col1, row2, col2):
        # Check if the indices are within the grid boundaries
        if not (0 <= row1 < GRID_SIZE and 0 <= col1 < GRID_SIZE and
                0 <= row2 < GRID_SIZE and 0 <= col2 < GRID_SIZE):
            return False

        # Check if the candies are adjacent (horizontally or vertically)
        if abs(row1 - row2) + abs(col1 - col2) != 1:
            return False

        return True

    # Thêm debug để xác nhận kẹo bọc được tạo
    def find_matches(self):
        """Tìm tất cả các kẹo khớp nhau trong lưới"""
        matches = []
        has_matches = False
        special_candies = []  # Danh sách các kẹo đặc biệt sẽ được tạo
        
        # Kiểm tra khớp ngang
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 2):
                if (self.grid[row][col] is not None and self.grid[row][col+1] is not None and self.grid[row][col+2] is not None and
                    self.grid[row][col].candy_type == self.grid[row][col+1].candy_type == self.grid[row][col+2].candy_type and
                    not self.grid[row][col].chocolate and not self.grid[row][col+1].chocolate and not self.grid[row][col+2].chocolate and
                    not self.grid[row][col].ingredient and not self.grid[row][col+1].ingredient and not self.grid[row][col+2].ingredient and
                    self.can_match(row, col) and self.can_match(row, col+1) and self.can_match(row, col+2)):
                    
                    # Đánh dấu k���o để xóa
                    match_length = 3
                    while col + match_length < GRID_SIZE and self.grid[row][col+match_length] is not None and \
                          self.grid[row][col].candy_type == self.grid[row][col+match_length].candy_type and \
                          self.can_match(row, col+match_length):
                        match_length += 1
                    
                    # Đánh dấu tất cả kẹo trong chuỗi khớp để xóa
                    for i in range(match_length):
                        self.grid[row][col+i].remove = True
                        
                        # Xử lý nút chặn
                        self.handle_blocker(row, col+i)
                    
                    # Tạo kẹo đặc biệt nếu khớp dài hơn 3
                    if match_length == 4:
                        # Tạo kẹo sọc
                        special_pos = col + random.randint(0, 3)
                        special_candies.append((row, special_pos, SpecialType.STRIPED_H))
                        print(f"Tạo kẹo sọc ngang tại ({row}, {special_pos})")
                    elif match_length >= 5:
                        # Tạo bom màu
                        special_pos = col + random.randint(0, match_length - 1)
                        special_candies.append((row, special_pos, SpecialType.COLOR_BOMB))
                        print(f"Tạo bom màu tại ({row}, {special_pos})")
                    
                    has_matches = True
        
        # Kiểm tra khớp dọc
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE - 2):
                if (self.grid[row][col] is not None and self.grid[row+1][col] is not None and self.grid[row+2][col] is not None and
                    self.grid[row][col].candy_type == self.grid[row+1][col].candy_type == self.grid[row+2][col].candy_type and
                    not self.grid[row][col].chocolate and not self.grid[row+1][col].chocolate and not self.grid[row+2][col].chocolate and
                    not self.grid[row][col].ingredient and not self.grid[row+1][col].ingredient and not self.grid[row+2][col].ingredient and
                    self.can_match(row, col) and self.can_match(row+1, col) and self.can_match(row+2, col)):
                    
                    # Đánh dấu kẹo để xóa
                    match_length = 3
                    while row + match_length < GRID_SIZE and self.grid[row+match_length][col] is not None and \
                          self.grid[row][col].candy_type == self.grid[row+match_length][col].candy_type and \
                          self.can_match(row+match_length, col):
                        match_length += 1
                    
                    # Đánh dấu tất cả kẹo trong chuỗi khớp để xóa
                    for i in range(match_length):
                        self.grid[row+i][col].remove = True
                        
                        # Xử lý nút chặn
                        self.handle_blocker(row+i, col)
                    
                    # Tạo kẹo đặc biệt nếu khớp dài hơn 3
                    if match_length == 4:
                        # Tạo kẹo sọc
                        special_pos = row + random.randint(0, 3)
                        special_candies.append((special_pos, col, SpecialType.STRIPED_V))
                        print(f"Tạo kẹo sọc dọc tại ({special_pos}, {col})")
                    elif match_length >= 5:
                        # Tạo bom màu
                        special_pos = row + random.randint(0, match_length - 1)
                        special_candies.append((special_pos, col, SpecialType.COLOR_BOMB))
                        print(f"Tạo bom màu tại ({special_pos}, {col})")
                    
                    has_matches = True
        
        # Kiểm tra hình chữ T và L cho kẹo bọc
        for row in range(1, GRID_SIZE - 1):
            for col in range(1, GRID_SIZE - 1):
                # Kiểm tra hình chữ T và L
                shapes = [
                    # Hình chữ T
                    [(0, -1), (0, 0), (0, 1), (-1, 0), (1, 0)],  # ┳
                    [(0, -1), (0, 0), (0, 1), (-1, 0), (-2, 0)],  # ┣
                    [(0, -1), (0, 0), (0, 1), (1, 0), (2, 0)],  # ┫
                    [(-1, 0), (0, 0), (1, 0), (0, -1), (0, -2)],  # ┻
                    
                    # Hình chữ L
                    [(-2, 0), (-1, 0), (0, 0), (0, 1), (0, 2)],  # ┌
                    [(0, -2), (0, -1), (0, 0), (1, 0), (2, 0)],  # ┘
                    [(-2, 0), (-1, 0), (0, 0), (0, -1), (0, -2)],  # ┐
                    [(0, -2), (0, -1), (0, 0), (-1, 0), (-2, 0)]   # └
                ]
                
                for shape in shapes:
                    valid_shape = True
                    candy_type = None
                    
                    for dr, dc in shape:
                        r, c = row + dr, col + dc
                        if not (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE):
                            valid_shape = False
                            break
                        
                        if self.grid[r][c] is None or self.grid[r][c].chocolate or self.grid[r][c].ingredient or not self.can_match(r, c):
                            valid_shape = False
                            break
                            
                        if candy_type is None:
                            candy_type = self.grid[r][c].candy_type
                        elif self.grid[r][c].candy_type != candy_type:
                            valid_shape = False
                            break
                    
                    if valid_shape:
                        # Đánh dấu kẹo để xóa và tạo kẹo bọc
                        for dr, dc in shape:
                            r, c = row + dr, col + dc
                            self.grid[r][c].remove = True
                            
                            # Xử lý nút chặn
                            self.handle_blocker(r, c)
                        
                        # Tạo kẹo bọc ở trung tâm
                        special_candies.append((row, col, SpecialType.WRAPPED))
                        has_matches = True
                        # Thêm debug để xác nhận kẹo bọc được tạo
                        print(f"Tạo kẹo bọc tại vị trí ({row}, {col}) với màu {candy_type.name}")
        
        # Tạo các kẹo đặc biệt sau khi đã đánh dấu tất cả các kẹo khớp
        for row, col, special_type in special_candies:
            # Lưu lại loại kẹo gốc
            candy_type = self.grid[row][col].candy_type
            
            # Đặt loại đặc biệt và bỏ đánh dấu xóa
            self.grid[row][col].special_type = special_type
            self.grid[row][col].remove = False
            print(f"Đã tạo kẹo đặc biệt {special_type.name} tại ({row}, {col}) với màu {candy_type.name}")
        
        return has_matches

    def can_match(self, row, col):
        if self.grid[row][col].blocker_type != BlockerType.NONE or self.grid[row][col].chocolate or self.grid[row][col].ingredient:
            return False
        return True

    def handle_blocker(self, row, col):
        if self.grid[row][col].blocker_type == BlockerType.SINGLE:
            self.grid[row][col] = None
        elif self.grid[row][col].blocker_type == BlockerType.DOUBLE:
            self.grid[row][col].blocker_type = BlockerType.SINGLE

    def remove_matches(self):
        points = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] and self.grid[row][col].remove:
                    points += 10
                    self.grid[row][col] = None
        self.score += points

    def move_candies_down(self):
        for col in range(GRID_SIZE):
            empty_spaces = []
            for row in range(GRID_SIZE - 1, -1, -1):
                if self.grid[row][col] is None:
                    empty_spaces.append(row)
                else:
                    if empty_spaces:
                        new_row = empty_spaces.pop(0)
                        self.grid[new_row][col] = self.grid[row][col]
                        self.grid[row][col] = None
                        empty_spaces.append(row)

    def fill_empty_spaces(self):
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    self.grid[row][col] = self.create_random_candy()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    self.handle_click(row, col)

            if self.find_matches():
                self.remove_matches()
                self.move_candies_down()
                self.fill_empty_spaces()

            self.draw_grid()
            self.draw_score()
            pygame.display.flip()

        pygame.quit()
