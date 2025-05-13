from constants import *

class CandyMovement:
    """
    Lớp chứa các thuật toán di chuyển kẹo, tách biệt khỏi logic cấp độ
    """
    
    @staticmethod
    def shift_candies_down(grid):
        """
        Di chuyển kẹo xuống để lấp đầy khoảng trống
        
        Args:
            grid: Lưới kẹo 2D
            
        Returns:
            bool: True nếu có bất kỳ kẹo nào di chuyển
        """
        any_moved = False
        
        for col in range(GRID_SIZE):
            # Đếm số ô trống trong mỗi cột
            empty_spaces = 0
            for row in range(GRID_SIZE - 1, -1, -1):
                if grid[row][col] is None or (grid[row][col].remove and grid[row][col].blocker_type == BlockerType.NONE):
                    empty_spaces += 1
                    if grid[row][col] is not None:
                        grid[row][col] = None
                elif empty_spaces > 0 and grid[row][col].blocker_type != BlockerType.STONE:
                    # Di chuyển kẹo xuống nếu không phải là đá
                    new_row = row + empty_spaces
                    grid[new_row][col] = grid[row][col]
                    grid[row][col] = None
                    grid[new_row][col].row = new_row
                    grid[new_row][col].target_y = GRID_OFFSET_Y + new_row * CELL_SIZE
                    any_moved = True
        
        return any_moved
    
    @staticmethod
    def shift_ingredients_down(grid, ingredients_left):
        """
        Di chuyển nguyên liệu xuống, xử lý trường hợp đặc biệt cho cấp độ nguyên liệu
        
        Args:
            grid: Lưới kẹo 2D
            ingredients_left: Số nguyên liệu còn lại
            
        Returns:
            tuple: (bool, int) - (có di chuyển không, số nguyên liệu còn lại)
        """
        any_moved = False
        remaining_ingredients = ingredients_left
        
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE - 1, -1, -1):
                if grid[row][col] is not None and grid[row][col].ingredient:
                    # Kiểm tra xem nó có thể di chuyển xuống không
                    if row < GRID_SIZE - 1 and (grid[row + 1][col] is None or grid[row + 1][col].remove):
                        # Di chuyển nguyên liệu xuống
                        if row + 1 == GRID_SIZE - 1:  # Đã đến đáy
                            grid[row][col].ingredient = False
                            remaining_ingredients -= 1
                            any_moved = True
                        else:
                            # Di chuyển nguyên liệu xuống
                            if grid[row + 1][col] is None:
                                grid[row + 1][col] = grid[row][col]
                                grid[row][col] = None
                            else:  # Kẹo bên dưới được đánh dấu để xóa
                                grid[row + 1][col] = grid[row][col]
                                grid[row][col] = None
                            
                            grid[row + 1][col].row = row + 1
                            grid[row + 1][col].target_y = GRID_OFFSET_Y + (row + 1) * CELL_SIZE
                            any_moved = True
        
        return any_moved, remaining_ingredients
    
    @staticmethod
    def fill_empty_spaces(grid, get_random_candy_type):
        """
        Điền các ô trống với kẹo mới
        
        Args:
            grid: Lưới kẹo 2D
            get_random_candy_type: Hàm để lấy loại kẹo ngẫu nhiên
            
        Returns:
            bool: True nếu có bất kỳ ô trống nào được điền
        """
        from candy import Candy
        any_filled = False
        
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE):
                if grid[row][col] is None:
                    candy_type = get_random_candy_type(row, col)
                    grid[row][col] = Candy(row, col, candy_type)
                    # Bắt đầu từ trên lưới
                    grid[row][col].y = GRID_OFFSET_Y - (GRID_SIZE - row) * CELL_SIZE
                    grid[row][col].target_y = GRID_OFFSET_Y + row * CELL_SIZE
                    any_filled = True
        
        return any_filled
    
    @staticmethod
    def swap_candies(grid, row1, col1, row2, col2):
        """
        Hoán đổi hai kẹo trong lưới
        
        Args:
            grid: Lưới kẹo 2D
            row1, col1: Vị trí của kẹo thứ nhất
            row2, col2: Vị trí của kẹo thứ hai
            
        Returns:
            bool: True nếu hoán đổi thành công
        """
        # Kiểm tra nút chặn
        if (grid[row1][col1].blocker_type in [BlockerType.STONE, BlockerType.LOCK, BlockerType.LICORICE] or
            grid[row2][col2].blocker_type in [BlockerType.STONE, BlockerType.LOCK, BlockerType.LICORICE]):
            return False  # Không thể hoán đổi kẹo bị chặn
        
        # Cập nhật vị trí đích
        grid[row1][col1].target_x = GRID_OFFSET_X + col2 * CELL_SIZE
        grid[row1][col1].target_y = GRID_OFFSET_Y + row2 * CELL_SIZE
        grid[row2][col2].target_x = GRID_OFFSET_X + col1 * CELL_SIZE
        grid[row2][col2].target_y = GRID_OFFSET_Y + row1 * CELL_SIZE
        
        # Hoán đổi vị trí trong lưới
        grid[row1][col1], grid[row2][col2] = grid[row2][col2], grid[row1][col1]
        
        # Cập nhật thuộc tính hàng và cột
        grid[row1][col1].row, grid[row1][col1].col = row2, col2
        grid[row2][col2].row, grid[row2][col2].col = row1, col1
        
        return True
