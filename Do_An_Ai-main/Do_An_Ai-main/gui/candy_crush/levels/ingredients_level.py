import random
from .base_level import BaseLevel
from constants import LevelType, GRID_SIZE, GRID_OFFSET_Y, CELL_SIZE

class IngredientsLevel(BaseLevel):
    def __init__(self, level_number):
        super().__init__(level_number)
        self.level_type = LevelType.INGREDIENTS
        # Giảm số lượng nguyên liệu từ 2 xuống 1
        self.ingredients_left = 1
    
    def initialize(self):
        super().initialize()
        
        # Thêm nguyên liệu ở phía trên
        for i in range(self.ingredients_left):
            col = random.randint(0, GRID_SIZE - 1)
            self.grid[0][col].ingredient = True
        # Don't reset moves_left here
    
    def shift_candies_down(self):
        """Di chuyển kẹo xuống để lấp đầy khoảng trống"""
        # Trước tiên xử lý nguyên liệu
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE - 1, -1, -1):
                if self.grid[row][col] is not None and self.grid[row][col].ingredient:
                    # Kiểm tra xem nó có thể di chuyển xuống không
                    if row < GRID_SIZE - 1 and (self.grid[row + 1][col] is None or self.grid[row + 1][col].remove):
                        # Di chuyển nguyên liệu xuống
                        if row + 1 == GRID_SIZE - 1:  # Đã đến đáy
                            self.grid[row][col].ingredient = False
                            self.ingredients_left -= 1
                        else:
                            # Di chuyển nguyên liệu xuống
                            if self.grid[row + 1][col] is None:
                                self.grid[row + 1][col] = self.grid[row][col]
                                self.grid[row][col] = None
                            else:  # Kẹo bên dưới được đánh dấu để xóa
                                self.grid[row + 1][col] = self.grid[row][col]
                                self.grid[row][col] = None
                            
                            self.grid[row + 1][col].row = row + 1
                            self.grid[row + 1][col].target_y = GRID_OFFSET_Y + (row + 1) * CELL_SIZE
        
        # Sau đó xử lý kẹo thường
        super().shift_candies_down()
    
    def is_level_complete(self):
        return self.ingredients_left <= 0
