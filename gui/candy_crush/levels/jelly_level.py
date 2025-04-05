import random
from .base_level import BaseLevel
from constants import LevelType, GRID_SIZE

class JellyLevel(BaseLevel):
    def __init__(self, level_number):
        super().__init__(level_number)
        self.level_type = LevelType.JELLY
        self.jellies_left = 15
    
    def initialize(self):
        super().initialize()
        
        # Thêm kẹo dẻo vào các vị trí ngẫu nhiên
        jelly_count = 0
        while jelly_count < self.jellies_left:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            if not self.grid[row][col].jelly:
                self.grid[row][col].jelly = True
                if random.random() < 0.3:  # 30% cơ hội cho kẹo dẻo đôi
                    self.grid[row][col].double_jelly = True
                jelly_count += 1
    
    def remove_matches(self):
        """Xóa các kẹo khớp nhau và cập nhật điểm"""
        # Đếm số kẹo khớp và cập nhật điểm
        match_count = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].remove:
                    match_count += 1
                    
                    # Xử lý kẹo dẻo
                    if self.grid[row][col].jelly:
                        if self.grid[row][col].double_jelly:
                            self.grid[row][col].double_jelly = False
                        else:
                            self.grid[row][col].jelly = False
                            self.jellies_left -= 1
                    
                    # Xử lý kẹo đặc biệt
                    self.handle_special_candy(row, col)
        
        # Cập nhật điểm
        self.score += match_count * 10
        
        # Xóa các kẹo khớp và di chuyển các kẹo còn lại xuống
        self.shift_candies_down()
        
        # Điền các ô trống với kẹo mới
        self.fill_empty_spaces()
    
    def is_level_complete(self):
        return self.jellies_left <= 0