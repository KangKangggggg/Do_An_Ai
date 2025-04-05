import random
from .base_level import BaseLevel
from constants import LevelType, GRID_SIZE

class ChocolateLevel(BaseLevel):
    def __init__(self, level_number):
        super().__init__(level_number)
        self.level_type = LevelType.CHOCOLATE
        self.chocolates_left = 10
    
    def initialize(self):
        super().initialize()
        
        # Thêm sô-cô-la vào các vị trí ngẫu nhiên
        chocolate_count = 0
        while chocolate_count < self.chocolates_left:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            if not self.grid[row][col].chocolate:
                self.grid[row][col].chocolate = True
                chocolate_count += 1
    
    def remove_matches(self):
        """Xóa các kẹo khớp nhau và cập nhật điểm"""
        # Đếm số kẹo khớp và cập nhật điểm
        match_count = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].remove:
                    match_count += 1
                    
                    # Xử lý sô-cô-la
                    if self.grid[row][col].chocolate:
                        self.grid[row][col].chocolate = False
                        self.chocolates_left -= 1
                    
                    # Xử lý kẹo đặc biệt
                    self.handle_special_candy(row, col)
        
        # Cập nhật điểm
        self.score += match_count * 10
        
        # Xóa các kẹo khớp và di chuyển các kẹo còn lại xuống
        self.shift_candies_down()
        
        # Điền các ô trống với kẹo mới
        self.fill_empty_spaces()
        
        # Lan rộng sô-cô-la
        self.spread_chocolate()
    
    def spread_chocolate(self):
        """Lan rộng sô-cô-la ngẫu nhiên đến các ô liền kề"""
        if random.random() < 0.3:  # 30% cơ hội lan rộng
            chocolate_spread = False
            while not chocolate_spread and self.chocolates_left > 0:
                # Tìm một sô-cô-la ngẫu nhiên
                chocolate_positions = []
                for row in range(GRID_SIZE):
                    for col in range(GRID_SIZE):
                        if self.grid[row][col].chocolate:
                            chocolate_positions.append((row, col))
                
                if chocolate_positions:
                    row, col = random.choice(chocolate_positions)
                    # Thử lan rộng theo một hướng ngẫu nhiên
                    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                    random.shuffle(directions)
                    
                    for dr, dc in directions:
                        new_row, new_col = row + dr, col + dc
                        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE and not self.grid[new_row][new_col].chocolate:
                            self.grid[new_row][new_col].chocolate = True
                            self.chocolates_left += 1
                            chocolate_spread = True
                            break
                else:
                    break  # Không có sô-cô-la để lan rộng
    
    def is_level_complete(self):
        return self.chocolates_left <= 0