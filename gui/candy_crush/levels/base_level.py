import random
from constants import *
from candy import Candy

class BaseLevel:
    def __init__(self, level_number):
        self.level_number = level_number
        self.score = 0
        self.moves_left = 20
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.target_score = 1000 * level_number
        
    def initialize(self):
        """Khởi tạo lưới cấp độ"""
        # Xóa lưới
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.grid[row][col] = None
        
        # Điền lưới với các kẹo ngẫu nhiên
        self.fill_grid()
    
    def fill_grid(self):
        """Điền lưới với các kẹo ngẫu nhiên"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    candy_type = self.get_random_candy_type(row, col)
                    self.grid[row][col] = Candy(row, col, candy_type)
        
        # Kiểm tra các kẹo khớp nhau khi bắt đầu và điền lại nếu cần
        while self.find_matches():
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.grid[row][col].remove:
                        candy_type = self.get_random_candy_type(row, col)
                        self.grid[row][col] = Candy(row, col, candy_type)
    
    def get_random_candy_type(self, row, col):
        """Lấy một loại kẹo ngẫu nhiên không tạo ra sự khớp"""
        # Tránh tạo ra các kẹo khớp nhau khi tạo kẹo ngẫu nhiên
        available_types = list(CandyType)
        
        # Kiểm tra khớp ngang
        if col >= 2:
            if (self.grid[row][col-1] is not None and 
                self.grid[row][col-2] is not None and
                self.grid[row][col-1].candy_type == self.grid[row][col-2].candy_type):
                if self.grid[row][col-1].candy_type in available_types:
                    available_types.remove(self.grid[row][col-1].candy_type)
        
        # Kiểm tra khớp dọc
        if row >= 2:
            if (self.grid[row-1][col] is not None and 
                self.grid[row-2][col] is not None and
                self.grid[row-1][col].candy_type == self.grid[row-2][col].candy_type):
                if self.grid[row-1][col].candy_type in available_types:
                    available_types.remove(self.grid[row-1][col].candy_type)
        
        return random.choice(available_types)
    
    def find_matches(self):
        """Tìm tất cả các kẹo khớp nhau trong lưới"""
        has_matches = False
        
        # Kiểm tra khớp ngang
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 2):
                if (self.grid[row][col].candy_type == self.grid[row][col+1].candy_type == self.grid[row][col+2].candy_type and
                    not self.grid[row][col].chocolate and not self.grid[row][col+1].chocolate and not self.grid[row][col+2].chocolate and
                    not self.grid[row][col].ingredient and not self.grid[row][col+1].ingredient and not self.grid[row][col+2].ingredient):
                    
                    # Đánh dấu kẹo để xóa
                    match_length = 3
                    while col + match_length < GRID_SIZE and self.grid[row][col].candy_type == self.grid[row][col+match_length].candy_type:
                        match_length += 1
                    
                    for i in range(match_length):
                        self.grid[row][col+i].remove = True
                    
                    # Tạo kẹo đặc biệt nếu khớp dài hơn 3
                    if match_length == 4:
                        # Tạo kẹo sọc
                        special_pos = col + random.randint(0, 3)
                        self.grid[row][special_pos].special_type = SpecialType.STRIPED_H
                    elif match_length >= 5:
                        # Tạo bom màu
                        special_pos = col + random.randint(0, 4)
                        self.grid[row][special_pos].special_type = SpecialType.COLOR_BOMB
                    
                    has_matches = True
        
        # Kiểm tra khớp dọc
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE - 2):
                if (self.grid[row][col].candy_type == self.grid[row+1][col].candy_type == self.grid[row+2][col].candy_type and
                    not self.grid[row][col].chocolate and not self.grid[row+1][col].chocolate and not self.grid[row+2][col].chocolate and
                    not self.grid[row][col].ingredient and not self.grid[row+1][col].ingredient and not self.grid[row+2][col].ingredient):
                    
                    # Đánh dấu kẹo để xóa
                    match_length = 3
                    while row + match_length < GRID_SIZE and self.grid[row][col].candy_type == self.grid[row+match_length][col].candy_type:
                        match_length += 1
                    
                    for i in range(match_length):
                        self.grid[row+i][col].remove = True
                    
                    # Tạo kẹo đặc biệt nếu khớp dài hơn 3
                    if match_length == 4:
                        # Tạo kẹo sọc
                        special_pos = row + random.randint(0, 3)
                        self.grid[special_pos][col].special_type = SpecialType.STRIPED_V
                    elif match_length >= 5:
                        # Tạo bom màu
                        special_pos = row + random.randint(0, 4)
                        self.grid[special_pos][col].special_type = SpecialType.COLOR_BOMB
                    
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
                        
                        if self.grid[r][c].chocolate or self.grid[r][c].ingredient:
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
                        
                        # Tạo kẹo bọc ở trung tâm
                        self.grid[row][col].special_type = SpecialType.WRAPPED
                        has_matches = True
        
        return has_matches
    
    def remove_matches(self):
        """Xóa các kẹo khớp nhau và cập nhật điểm"""
        # Đếm số kẹo khớp và cập nhật điểm
        match_count = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].remove:
                    match_count += 1
                    
                    # Xử lý kẹo đặc biệt
                    self.handle_special_candy(row, col)
        
        # Cập nhật điểm
        self.score += match_count * 10
        
        # Xóa các kẹo khớp và di chuyển các kẹo còn lại xuống
        self.shift_candies_down()
        
        # Điền các ô trống với kẹo mới
        self.fill_empty_spaces()
    
    def handle_special_candy(self, row, col):
        """Xử lý hiệu ứng kẹo đặc biệt"""
        if self.grid[row][col].special_type == SpecialType.STRIPED_H:
            # Xóa toàn bộ hàng
            for c in range(GRID_SIZE):
                if c != col:
                    self.grid[row][c].remove = True
        
        elif self.grid[row][col].special_type == SpecialType.STRIPED_V:
            # Xóa toàn bộ cột
            for r in range(GRID_SIZE):
                if r != row:
                    self.grid[r][col].remove = True
        
        elif self.grid[row][col].special_type == SpecialType.WRAPPED:
            # Xóa khu vực 3x3
            for r in range(max(0, row-1), min(GRID_SIZE, row+2)):
                for c in range(max(0, col-1), min(GRID_SIZE, col+2)):
                    if not (r == row and c == col):
                        self.grid[r][c].remove = True
        
        elif self.grid[row][col].special_type == SpecialType.COLOR_BOMB:
            # Xóa tất cả kẹo cùng màu
            candy_type = self.grid[row][col].candy_type
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.grid[r][c].candy_type == candy_type:
                        self.grid[r][c].remove = True
    
    def shift_candies_down(self):
        """Di chuyển kẹo xuống để lấp đầy khoảng trống"""
        for col in range(GRID_SIZE):
            # Đếm số ô trống trong mỗi cột
            empty_spaces = 0
            for row in range(GRID_SIZE - 1, -1, -1):
                if self.grid[row][col].remove:
                    empty_spaces += 1
                    self.grid[row][col] = None
                elif empty_spaces > 0:
                    # Di chuyển kẹo xuống
                    new_row = row + empty_spaces
                    self.grid[new_row][col] = self.grid[row][col]
                    self.grid[row][col] = None
                    self.grid[new_row][col].row = new_row
                    self.grid[new_row][col].target_y = GRID_OFFSET_Y + new_row * CELL_SIZE
    
    def fill_empty_spaces(self):
        """Điền các ô trống với kẹo mới"""
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    candy_type = self.get_random_candy_type(row, col)
                    self.grid[row][col] = Candy(row, col, candy_type)
                    # Bắt đầu từ trên lưới
                    self.grid[row][col].y = GRID_OFFSET_Y - (GRID_SIZE - row) * CELL_SIZE
                    self.grid[row][col].target_y = GRID_OFFSET_Y + row * CELL_SIZE
    
    def swap_candies(self, row1, col1, row2, col2):
        """Hoán đổi hai kẹo trong lưới"""
        # Cập nhật vị trí đích
        self.grid[row1][col1].target_x = GRID_OFFSET_X + col2 * CELL_SIZE
        self.grid[row1][col1].target_y = GRID_OFFSET_Y + row2 * CELL_SIZE
        self.grid[row2][col2].target_x = GRID_OFFSET_X + col1 * CELL_SIZE
        self.grid[row2][col2].target_y = GRID_OFFSET_Y + row1 * CELL_SIZE
        
        # Hoán đổi vị trí trong lưới
        self.grid[row1][col1], self.grid[row2][col2] = self.grid[row2][col2], self.grid[row1][col1]
        
        # Cập nhật thuộc tính hàng và cột
        self.grid[row1][col1].row, self.grid[row1][col1].col = row1, col1
        self.grid[row2][col2].row, self.grid[row2][col2].col = row2, col2
    
    def is_level_complete(self):
        """Kiểm tra xem cấp độ đã hoàn thành chưa"""
        return self.score >= self.target_score
    
    def update_candies(self):
        """Cập nhật tất cả kẹo trong lưới"""
        any_moving = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is not None:
                    self.grid[row][col].update()
                    if self.grid[row][col].moving:
                        any_moving = True
        return any_moving
    
    def draw_candies(self, screen):
        """Vẽ tất cả kẹo trong lưới"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is not None:
                    self.grid[row][col].draw(screen)