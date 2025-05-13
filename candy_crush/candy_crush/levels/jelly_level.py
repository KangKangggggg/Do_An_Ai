import random
from .base_level import BaseLevel
from constants import LevelType, GRID_SIZE
from constants import SpecialType, GRID_OFFSET_Y, CELL_SIZE, GRID_OFFSET_X, BlockerType

class JellyLevel(BaseLevel):
    def __init__(self, level_number):
        super().__init__(level_number)
        self.level_type = LevelType.JELLY
        # Giảm số lượng kẹo dẻo từ 6 xuống 2 để dễ hơn
        self.jellies_left = 4
    
    def initialize(self):
        super().initialize()
        
        # Reset số lượng kẹo dẻo trước
        self.jellies_left = 2  # Chỉ 2 kẹo dẻo
        
        # Xóa bất kỳ kẹo dẻo hiện có
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.grid[row][col].jelly = False
                self.grid[row][col].double_jelly = False
        
        # Thêm kẹo dẻo vào các vị trí dễ tiếp cận
        # Đặt kẹo dẻo ở giữa bảng để dễ tiếp cận
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
        # Không reset moves_left ở đây
    
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
        
        # Tăng điểm thưởng để dễ đạt mục tiêu
        self.score += match_count * 20  # Tăng từ 15 lên 20
        
        # Xóa các kẹo khớp và di chuyển các kẹo còn lại xuống
        self.shift_candies_down()
        
        # Điền các ô trống với kẹo mới
        self.fill_empty_spaces()
    
    def shift_candies_down(self):
        """Di chuyển kẹo xuống để lấp đầy khoảng trống và giữ lại thuộc tính kẹo dẻo"""
        # Đánh dấu tất cả các kẹo đã được xóa
        removed_count = 0
        
        # Lưu trữ thông tin về kẹo dẻo theo vị trí lưới
        jelly_positions = {}
        double_jelly_positions = {}
        
        # Lưu lại vị trí của các ô kẹo dẻo trước khi di chuyển kẹo
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is not None:
                    if self.grid[row][col].jelly:
                        jelly_positions[(row, col)] = True
                    if self.grid[row][col].double_jelly:
                        double_jelly_positions[(row, col)] = True
                    
                    if self.grid[row][col].remove:
                        self.grid[row][col] = None
                        removed_count += 1
        
        print(f"Đã xóa {removed_count} kẹo khỏi lưới")
        
        # Xử lý từng cột một, từ dưới lên trên
        for col in range(GRID_SIZE):
            # Đếm số ô trống trong mỗi cột
            empty_spaces = []
            for row in range(GRID_SIZE-1, -1, -1):
                if self.grid[row][col] is None:
                    empty_spaces.append(row)
                elif empty_spaces and self.grid[row][col].blocker_type != BlockerType.STONE:
                    # Nếu có ô trống và kẹo hiện tại không phải là đá, di chuyển kẹo xuống
                    target_row = empty_spaces.pop(0)
                    
                    # Di chuyển kẹo
                    self.grid[target_row][col] = self.grid[row][col]
                    self.grid[row][col] = None
                    
                    # Cập nhật vị trí của kẹo
                    self.grid[target_row][col].row = target_row
                    self.grid[target_row][col].col = col
                    self.grid[target_row][col].target_y = GRID_OFFSET_Y + target_row * CELL_SIZE
                    self.grid[target_row][col].target_x = GRID_OFFSET_X + col * CELL_SIZE
                    
                    # Xóa thuộc tính kẹo dẻo khỏi kẹo đã di chuyển
                    self.grid[target_row][col].jelly = False
                    self.grid[target_row][col].double_jelly = False
                    
                    # Thêm vị trí cũ vào danh sách ô trống
                    empty_spaces.append(row)
                    # Sắp xếp lại danh sách ô trống theo thứ tự giảm dần
                    empty_spaces.sort(reverse=True)
        
        # Khôi phục thuộc tính kẹo dẻo cho các ô theo vị trí lưới ban đầu
        for (row, col), has_jelly in jelly_positions.items():
            if self.grid[row][col] is not None:
                self.grid[row][col].jelly = has_jelly
                
        for (row, col), has_double_jelly in double_jelly_positions.items():
            if self.grid[row][col] is not None:
                self.grid[row][col].double_jelly = has_double_jelly
        
        # Kiểm tra xem còn ô trống nào không
        empty_count = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    empty_count += 1
        
        print(f"Sau khi di chuyển kẹo xuống, còn {empty_count} ô trống")
    
    def is_level_complete(self):
        # Cấp độ hoàn thành khi tất cả kẹo dẻo đã bị loại bỏ
        complete = self.jellies_left <= 0
        print(f"Checking if jelly level is complete: jellies_left={self.jellies_left}, complete={complete}")
        # Điểm số không quan trọng trong cấp độ kẹo dẻo, chỉ cần loại bỏ hết kẹo dẻo
        return complete
    
    # Ghi đè phương thức tìm khớp để tăng tỷ lệ tạo kẹo đặc biệt
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
