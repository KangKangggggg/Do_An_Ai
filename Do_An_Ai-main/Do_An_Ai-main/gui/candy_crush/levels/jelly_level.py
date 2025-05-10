import random
from .base_level import BaseLevel
from constants import LevelType, GRID_SIZE
from constants import SpecialType

class JellyLevel(BaseLevel):
    def __init__(self, level_number):
        super().__init__(level_number)
        self.level_type = LevelType.JELLY
        # Giảm số lượng kẹo dẻo từ 6 xuống 2 để dễ hơn
        self.jellies_left = 2
    
    def initialize(self):
        super().initialize()
        
        # Reset jellies count first
        self.jellies_left = 2  # Chỉ 2 kẹo dẻo
        
        # Clear any existing jellies
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.grid[row][col].jelly = False
                self.grid[row][col].double_jelly = False
        
        # Thêm kẹo dẻo vào các vị trí dễ tiếp cận
        # Đặt kẹo dẻo ở vị trí dễ thấy và dễ khớp
        middle_row = GRID_SIZE // 2
        middle_col = GRID_SIZE // 2
        
        # Đặt kẹo dẻo ở giữa bảng để dễ tiếp cận
        self.grid[middle_row][middle_col].jelly = True
        print(f"Added jelly at center [{middle_row}][{middle_col}]")
        
        # Đặt kẹo dẻo thứ hai gần với kẹo đầu tiên
        self.grid[middle_row][middle_col + 1].jelly = True
        print(f"Added jelly at [{middle_row}][{middle_col + 1}]")
        
        # Không sử dụng kẹo dẻo đôi để dễ hơn
        
        print(f"Initialized jelly level with {self.jellies_left} jellies at easy-to-reach positions")
        # Don't reset moves_left here
    
    def remove_matches(self):
        """Xóa các kẹo khớp nhau và cập nhật điểm"""
        # Đếm số kẹo khớp và cập nhật điểm
        match_count = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is not None and self.grid[row][col].remove:
                    match_count += 1
                    
                    # Xử lý kẹo dẻo
                    if self.grid[row][col].jelly:
                        if self.grid[row][col].double_jelly:
                            self.grid[row][col].double_jelly = False
                            print(f"Removed double jelly at [{row}][{col}], jellies left: {self.jellies_left}")
                        else:
                            self.grid[row][col].jelly = False
                            self.jellies_left -= 1
                            print(f"Removed jelly at [{row}][{col}], jellies left: {self.jellies_left}")
                    
                    # Xử lý kẹo đặc biệt
                    if self.grid[row][col].special_type != SpecialType.NORMAL:
                        self.handle_special_candy(row, col)
        
        # Tăng điểm thưởng - tăng điểm thưởng để dễ đạt mục tiêu
        self.score += match_count * 20  # Tăng từ 15 lên 20
        
        # Xóa các kẹo khớp và di chuyển các kẹo còn lại xuống
        self.shift_candies_down()
        
        # Điền các ô trống với kẹo mới
        self.fill_empty_spaces()
    
    def is_level_complete(self):
        complete = self.jellies_left <= 0
        print(f"Checking if jelly level is complete: jellies_left={self.jellies_left}, complete={complete}")
        return complete
    
    # Thêm phương thức để tăng tỷ lệ tạo kẹo đặc biệt
    def find_matches(self):
        """Ghi đè phương thức tìm khớp để tăng tỷ lệ tạo kẹo đặc biệt"""
        has_matches = super().find_matches()
        
        # Thêm cơ hội ngẫu nhiên để tạo kẹo đặc biệt ngay cả khi không có khớp dài
        if has_matches and random.random() < 0.2:  # 20% cơ hội
            # Tìm một kẹo đã được đánh dấu để xóa và biến nó thành kẹo đặc biệt
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.grid[row][col] is not None and self.grid[row][col].remove:
                        # Chọn ngẫu nhiên một loại kẹo đặc biệt
                        special_types = [SpecialType.STRIPED_H, SpecialType.STRIPED_V, SpecialType.WRAPPED]
                        special_type = random.choice(special_types)
                        
                        # Đặt loại đặc biệt và bỏ đánh dấu xóa
                        self.grid[row][col].special_type = special_type
                        self.grid[row][col].remove = False
                        print(f"Randomly created special candy {special_type.name} at [{row}][{col}]")
                        break
                else:
                    continue
                break
        
        return has_matches
