import random
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import *
from candy import Candy

class BaseLevel:
    def __init__(self, level_number):
        self.level_number = level_number
        self.score = 0
        self.moves_left = 30
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.target_score = 800 * level_number
        self.blockers_count = 0  # Số lượng nút chặn trong cấp độ
        self.wrapped_explosion_pending = []  # Danh sách các kẹo bọc đang chờ nổ lần thứ hai
        
    def initialize(self):
        """Khởi tạo lưới cấp độ"""
        # Xóa lưới
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.grid[row][col] = None
        
        # Điền lưới với các kẹo ngẫu nhiên
        self.fill_grid()
        
        # Thêm các nút chặn dựa trên cấp độ
        self.add_blockers()
        
        # Xóa danh sách kẹo bọc đang chờ nổ
        self.wrapped_explosion_pending = []
        
        # IMPORTANT: Don't reset moves_left here, as it's set by the game
    
    def add_blockers(self):
        """Thêm các nút chặn vào lưới dựa trên cấp độ"""
        self.blockers_count = 0
        
        # Cấp độ càng cao, càng nhiều nút chặn
        num_blockers = min(10, self.level_number * 2)
        
        # Xác định loại nút chặn dựa trên cấp độ
        available_blockers = []
        
        if self.level_number >= 1:
            available_blockers.append(BlockerType.ICE)
        
        if self.level_number >= 3:
            available_blockers.append(BlockerType.STONE)
        
        if self.level_number >= 5:
            available_blockers.append(BlockerType.LOCK)
        
        if self.level_number >= 7:
            available_blockers.append(BlockerType.LICORICE)
        
        if not available_blockers:
            return
        
        # Thêm nút chặn ngẫu nhiên
        for _ in range(num_blockers):
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            
            # Không đặt nút chặn ở các góc
            if (row == 0 and col == 0) or (row == 0 and col == GRID_SIZE - 1) or \
               (row == GRID_SIZE - 1 and col == 0) or (row == GRID_SIZE - 1 and col == GRID_SIZE - 1):
                continue
            
            blocker_type = random.choice(available_blockers)
            
            if blocker_type == BlockerType.ICE:
                self.grid[row][col].blocker_type = BlockerType.ICE
                self.grid[row][col].blocker_health = random.randint(1, 2)  # 1 hoặc 2 lớp băng
                self.blockers_count += 1
            
            elif blocker_type == BlockerType.STONE:
                self.grid[row][col].blocker_type = BlockerType.STONE
                self.grid[row][col].blocker_health = 1
                self.blockers_count += 1
            
            elif blocker_type == BlockerType.LOCK:
                self.grid[row][col].blocker_type = BlockerType.LOCK
                self.grid[row][col].blocker_health = 1
                self.blockers_count += 1
            
            elif blocker_type == BlockerType.LICORICE:
                self.grid[row][col].blocker_type = BlockerType.LICORICE
                self.grid[row][col].blocker_health = 1
                self.blockers_count += 1
    
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
        special_candies = []  # Danh sách các kẹo đặc biệt sẽ được tạo
        
        # Kiểm tra khớp ngang
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 2):
                if (self.grid[row][col] is not None and self.grid[row][col+1] is not None and self.grid[row][col+2] is not None and
                    self.grid[row][col].candy_type == self.grid[row][col+1].candy_type == self.grid[row][col+2].candy_type and
                    not self.grid[row][col].chocolate and not self.grid[row][col+1].chocolate and not self.grid[row][col+2].chocolate and
                    not self.grid[row][col].ingredient and not self.grid[row][col+1].ingredient and not self.grid[row][col+2].ingredient and
                    self.can_match(row, col) and self.can_match(row, col+1) and self.can_match(row, col+2)):
                    
                    # Đánh dấu kẹo để xóa
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
                        # Tạo kẹo sọc ngang (vì khớp ngang)
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
                        # Tạo kẹo sọc dọc (vì khớp dọc)
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
        
        # Tạo các kẹo đặc biệt sau khi đã đánh dấu tất cả các kẹo khớp
        for row, col, special_type in special_candies:
            # Lưu lại loại kẹo gốc
            if self.grid[row][col] is not None:
                candy_type = self.grid[row][col].candy_type
                
                # Đặt loại đặc biệt và bỏ đánh dấu xóa
                self.grid[row][col].special_type = special_type
                self.grid[row][col].remove = False
                print(f"Đã tạo kẹo đặc biệt {special_type.name} tại ({row}, {col}) với màu {candy_type.name}")
        
        return has_matches
    
    def can_match(self, row, col):
        """Kiểm tra xem kẹo có thể khớp hay không (không bị chặn bởi nút chặn)"""
        # Kẹo có thể khớp nếu không có nút chặn hoặc nút chặn là băng
        if self.grid[row][col].blocker_type == BlockerType.NONE:
            return True
        elif self.grid[row][col].blocker_type == BlockerType.ICE:
            return True
        else:
            return False
    
    def handle_blocker(self, row, col):
        """Xử lý nút chặn khi kẹo bị khớp"""
        if self.grid[row][col].blocker_type != BlockerType.NONE:
            # Giảm sức khỏe của nút chặn
            self.grid[row][col].blocker_health -= 1
            
            # Nếu sức khỏe = 0, xóa nút chặn
            if self.grid[row][col].blocker_health <= 0:
                self.grid[row][col].blocker_type = BlockerType.NONE
                self.blockers_count -= 1
                self.score += 50  # Thêm điểm khi phá hủy nút chặn
            else:
                # Nếu vẫn còn sức khỏe, không xóa kẹo
                self.grid[row][col].remove = False
    
    def remove_matches(self):
        """Xóa các kẹo khớp nhau và cập nhật điểm"""
        # Đếm số kẹo khớp và cập nhật điểm
        match_count = 0
        
        # Xử lý kẹo bọc đang chờ nổ lần thứ hai
        pending_explosions = self.wrapped_explosion_pending.copy()
        self.wrapped_explosion_pending = []  # Xóa danh sách để tránh xử lý lặp lại
        
        for row, col in pending_explosions:
            if (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and 
                self.grid[row][col] is not None and 
                self.grid[row][col].special_type == SpecialType.WRAPPED):
                # Nổ lần thứ hai
                print(f"Kích hoạt nổ lần thứ hai cho kẹo bọc tại ({row}, {col})")
                self.explode_wrapped_candy(row, col, is_second_explosion=True)
    
        # Xử lý các kẹo khớp thông thường
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is not None and self.grid[row][col].remove:
                    match_count += 1
                    
                    # Xử lý kẹo đặc biệt
                    if self.grid[row][col].special_type != SpecialType.NORMAL:
                        self.handle_special_candy(row, col)
    
        # Tăng điểm thưởng cho mỗi kẹo khớp
        self.score += match_count * 15
        
        # Xóa các kẹo khớp và di chuyển các kẹo còn lại xuống
        self.shift_candies_down()
        
        # Điền các ô trống với kẹo mới
        self.fill_empty_spaces()
    
    def explode_wrapped_candy(self, row, col, is_second_explosion=False):
        """Kích hoạt nổ kẹo bọc"""
        print(f"Kích hoạt nổ kẹo bọc tại ({row}, {col}), lần nổ thứ {'hai' if is_second_explosion else 'nhất'}")
        
        # Xóa khu vực 3x3 xung quanh kẹo bọc
        for r in range(max(0, row-1), min(GRID_SIZE, row+2)):
            for c in range(max(0, col-1), min(GRID_SIZE, col+2)):
                if self.grid[r][c] is not None:
                    # Không xóa kẹo bọc gốc trong lần nổ đầu tiên
                    if not (r == row and c == col and not is_second_explosion):
                        self.grid[r][c].remove = True
                        self.score += 60  # Thêm điểm cho kẹo bị phá hủy bởi kẹo đặc biệt
                        
                        # Xử lý nút chặn
                        self.handle_blocker(r, c)
    
        # Nếu là lần nổ đầu tiên, thêm vào danh sách chờ nổ lần thứ hai
        if not is_second_explosion:
            self.wrapped_explosion_pending.append((row, col))
            # Không xóa kẹo bọc sau lần nổ đầu tiên
            self.grid[row][col].remove = False
        else:
            # Đảm bảo kẹo bọc được xóa sau lần nổ thứ hai
            if self.grid[row][col] is not None:
                self.grid[row][col].remove = True
    
    def handle_special_candy(self, row, col):
        """Xử lý hiệu ứng kẹo đặc biệt"""
        if self.grid[row][col].special_type == SpecialType.STRIPED_H:
            # Xóa toàn bộ hàng
            for c in range(GRID_SIZE):
                if self.grid[row][c] is not None and not self.grid[row][c].remove:
                    self.grid[row][c].remove = True
                    self.score += 60  # Thêm điểm cho kẹo bị phá hủy bởi kẹo đặc biệt
                    
                    # Xử lý nút chặn
                    self.handle_blocker(row, c)
    
        elif self.grid[row][col].special_type == SpecialType.STRIPED_V:
            # Xóa toàn bộ cột
            for r in range(GRID_SIZE):
                if self.grid[r][col] is not None and not self.grid[r][col].remove:
                    self.grid[r][col].remove = True
                    self.score += 60  # Thêm điểm cho kẹo bị phá hủy bởi kẹo đặc biệt
                    
                    # Xử lý nút chặn
                    self.handle_blocker(r, col)
    
        elif self.grid[row][col].special_type == SpecialType.WRAPPED:
            # Kích hoạt nổ kẹo bọc
            self.explode_wrapped_candy(row, col)
    
        elif self.grid[row][col].special_type == SpecialType.COLOR_BOMB:
            # Xóa tất cả kẹo cùng màu với kẹo màu
            candy_type = self.grid[row][col].candy_type
        
            # Tìm một màu ngẫu nhiên để xóa (vì kẹo màu không có màu cụ thể)
            available_types = []
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if (self.grid[r][c] is not None and 
                        not self.grid[r][c].remove and 
                        self.grid[r][c].special_type == SpecialType.NORMAL and
                        self.grid[r][c].candy_type not in available_types):
                        available_types.append(self.grid[r][c].candy_type)
        
            if available_types:
                target_type = random.choice(available_types)
            
                # Xóa tất cả kẹo cùng màu với màu đã chọn
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        if (self.grid[r][c] is not None and 
                            self.grid[r][c].candy_type == target_type and 
                            not self.grid[r][c].remove):
                            self.grid[r][c].remove = True
                            self.score += 100  # Thêm điểm cho kẹo bị phá hủy bởi bom màu
                            
                            # Xử lý nút chặn
                            self.handle_blocker(r, c)
    
    def check_special_combination(self, row1, col1, row2, col2):
        """Kiểm tra và xử lý kết hợp kẹo đặc biệt"""
        candy1 = self.grid[row1][col1]
        candy2 = self.grid[row2][col2]
    
        # Nếu có nút chặn khóa, không thể hoán đổi
        if (candy1.blocker_type == BlockerType.LOCK or candy1.blocker_type == BlockerType.STONE or 
            candy1.blocker_type == BlockerType.LICORICE or
            candy2.blocker_type == BlockerType.LOCK or candy2.blocker_type == BlockerType.STONE or 
            candy2.blocker_type == BlockerType.LICORICE):
            return False
    
        # Nếu cả hai kẹo đều là kẹo đặc biệt
        if candy1.special_type != SpecialType.NORMAL and candy2.special_type != SpecialType.NORMAL:
            # Kết hợp hai bom màu
            if candy1.special_type == SpecialType.COLOR_BOMB and candy2.special_type == SpecialType.COLOR_BOMB:
                # Xóa tất cả kẹo trên bảng
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        if self.grid[r][c] is not None and not self.grid[r][c].remove:
                            self.grid[r][c].remove = True
                            self.score += 300  # Điểm cao cho kết hợp mạnh nhất
                            
                            # Xử lý nút chặn
                            self.handle_blocker(r, c)
            
                candy1.remove = True
                candy2.remove = True
                return True
        
            # Kết hợp bom màu với kẹo sọc
            elif ((candy1.special_type == SpecialType.COLOR_BOMB and 
                  (candy2.special_type == SpecialType.STRIPED_H or candy2.special_type == SpecialType.STRIPED_V)) or
                 (candy2.special_type == SpecialType.COLOR_BOMB and 
                  (candy1.special_type == SpecialType.STRIPED_H or candy1.special_type == SpecialType.STRIPED_V))):
            
                # Xác định bom màu và kẹo sọc
                color_bomb = candy1 if candy1.special_type == SpecialType.COLOR_BOMB else candy2
                striped = candy2 if candy1.special_type == SpecialType.COLOR_BOMB else candy1
            
                # Biến tất cả kẹo cùng màu với kẹo sọc thành kẹo sọc và kích hoạt chúng
                target_type = striped.candy_type
                striped_type = striped.special_type
            
                # Danh sách các vị trí cần kích hoạt sau khi biến đổi
                positions_to_activate = []
            
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        if self.grid[r][c] is not None and self.grid[r][c].candy_type == target_type and not self.grid[r][c].remove:
                            # Biến thành kẹo sọc cùng loại
                            self.grid[r][c].special_type = striped_type
                            positions_to_activate.append((r, c))
            
                # Kích hoạt tất cả kẹo sọc đã biến đổi
                for r, c in positions_to_activate:
                    if striped_type == SpecialType.STRIPED_H:
                        # Kích hoạt kẹo sọc ngang
                        for cc in range(GRID_SIZE):
                            if self.grid[r][cc] is not None and not self.grid[r][cc].remove:
                                self.grid[r][cc].remove = True
                                self.score += 120
                                
                                # Xử lý nút chặn
                                self.handle_blocker(r, cc)
                    else:  # STRIPED_V
                        # Kích hoạt kẹo sọc dọc
                        for rr in range(GRID_SIZE):
                            if self.grid[rr][c] is not None and not self.grid[rr][c].remove:
                                self.grid[rr][c].remove = True
                                self.score += 120
                                
                                # Xử lý nút chặn
                                self.handle_blocker(rr, c)
            
                color_bomb.remove = True
                striped.remove = True
                return True
        
            # Kết hợp bom màu với kẹo bọc
            elif ((candy1.special_type == SpecialType.COLOR_BOMB and candy2.special_type == SpecialType.WRAPPED) or
                 (candy2.special_type == SpecialType.COLOR_BOMB and candy1.special_type == SpecialType.WRAPPED)):
            
                # Xác định bom màu và kẹo bọc
                color_bomb = candy1 if candy1.special_type == SpecialType.COLOR_BOMB else candy2
                wrapped = candy2 if candy1.special_type == SpecialType.COLOR_BOMB else candy1
            
                # Biến tất cả kẹo cùng màu với kẹo bọc thành kẹo bọc và kích hoạt chúng
                target_type = wrapped.candy_type
            
                # Danh sách các vị trí cần kích hoạt sau khi biến đổi
                positions_to_activate = []
            
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        if self.grid[r][c] is not None and self.grid[r][c].candy_type == target_type and not self.grid[r][c].remove:
                            # Biến thành kẹo bọc
                            self.grid[r][c].special_type = SpecialType.WRAPPED
                            positions_to_activate.append((r, c))
            
                # Kích hoạt tất cả kẹo bọc đã biến đổi
                for r, c in positions_to_activate:
                    # Kích hoạt hiệu ứng kẹo bọc (nổ 2 lần)
                    self.explode_wrapped_candy(r, c, is_second_explosion=False)
          
                color_bomb.remove = True
                wrapped.remove = True
                return True
        
            # Kết hợp hai kẹo sọc
            elif ((candy1.special_type == SpecialType.STRIPED_H or candy1.special_type == SpecialType.STRIPED_V) and
                 (candy2.special_type == SpecialType.STRIPED_H or candy2.special_type == SpecialType.STRIPED_V)):
            
                # Xóa tất cả kẹo trong hàng và cột
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        if (r == row1 or r == row2 or c == col1 or c == col2) and self.grid[r][c] is not None and not self.grid[r][c].remove:
                            self.grid[r][c].remove = True
                            self.score += 120
                            
                            # Xử lý nút chặn
                            self.handle_blocker(r, c)
            
                candy1.remove = True
                candy2.remove = True
                return True
        
            # Kết hợp kẹo sọc với kẹo bọc - tạo hình chữ thập lớn
            elif ((candy1.special_type == SpecialType.WRAPPED and 
                  (candy2.special_type == SpecialType.STRIPED_H or candy2.special_type == SpecialType.STRIPED_V)) or
                 (candy2.special_type == SpecialType.WRAPPED and 
                  (candy1.special_type == SpecialType.STRIPED_H or candy1.special_type == SpecialType.STRIPED_V))):
          
                # Xác định vị trí trung tâm
                center_row = row1
                center_col = col1
            
                # Xóa 3 hàng và 3 cột tạo thành hình chữ thập
                for r in range(max(0, center_row-1), min(GRID_SIZE, center_row+2)):
                    for c in range(GRID_SIZE):
                        if self.grid[r][c] is not None and not self.grid[r][c].remove:
                            self.grid[r][c].remove = True
                            self.score += 150
                            
                            # Xử lý nút chặn
                            self.handle_blocker(r, c)
            
                for c in range(max(0, center_col-1), min(GRID_SIZE, center_col+2)):
                    for r in range(GRID_SIZE):
                        if self.grid[r][c] is not None and not self.grid[r][c].remove:
                            self.grid[r][c].remove = True
                            self.score += 150
                            
                            # Xử lý nút chặn
                            self.handle_blocker(r, c)
          
                candy1.remove = True
                candy2.remove = True
                return True
        
            # Kết hợp hai kẹo bọc
            elif candy1.special_type == SpecialType.WRAPPED and candy2.special_type == SpecialType.WRAPPED:
                # Xóa kẹo trong khu vực 5x5 hai lần liên tiếp
                center_row = row1
                center_col = col1
            
                # Lần đầu tiên
                for r in range(max(0, center_row-2), min(GRID_SIZE, center_row+3)):
                    for c in range(max(0, center_col-2), min(GRID_SIZE, center_col+3)):
                        if self.grid[r][c] is not None and not self.grid[r][c].remove:
                            self.grid[r][c].remove = True
                            self.score += 125
                            
                            # Xử lý nút chặn
                            self.handle_blocker(r, c)
            
                # Lần thứ hai - trong Candy Crush gốc, nổ lần thứ hai xảy ra ngay lập tức
                for r in range(max(0, center_row-2), min(GRID_SIZE, center_row+3)):
                    for c in range(max(0, center_col-2), min(GRID_SIZE, center_col+3)):
                        if self.grid[r][c] is not None and not self.grid[r][c].remove:
                            self.grid[r][c].remove = True
                            self.score += 125
                            
                            # Xử lý nút chặn
                            self.handle_blocker(r, c)
            
                candy1.remove = True
                candy2.remove = True
                return True
    
        # Kết hợp bom màu với kẹo thường
        elif candy1.special_type == SpecialType.COLOR_BOMB or candy2.special_type == SpecialType.COLOR_BOMB:
            # Xác định bom màu và kẹo thường
            color_bomb = candy1 if candy1.special_type == SpecialType.COLOR_BOMB else candy2
            normal = candy2 if candy1.special_type == SpecialType.COLOR_BOMB else candy1
        
            # Xóa tất cả kẹo cùng màu với kẹo thường
            target_type = normal.candy_type
        
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.grid[r][c] is not None and self.grid[r][c].candy_type == target_type and not self.grid[r][c].remove:
                        self.grid[r][c].remove = True
                        self.score += 100
                        
                        # Xử lý nút chặn
                        self.handle_blocker(r, c)
        
            color_bomb.remove = True
            normal.remove = True
            return True
    
        return False
    
    def swap_candies(self, row1, col1, row2, col2):
        """Hoán đổi hai kẹo trong lưới"""
        # Kiểm tra nút chặn
        if (self.grid[row1][col1].blocker_type in [BlockerType.STONE, BlockerType.LOCK, BlockerType.LICORICE] or
            self.grid[row2][col2].blocker_type in [BlockerType.STONE, BlockerType.LOCK, BlockerType.LICORICE]):
            return False  # Không thể hoán đổi kẹo bị chặn
        
        # Kiểm tra kết hợp kẹo đặc biệt trước
        if self.check_special_combination(row1, col1, row2, col2):
            # Đã xử lý kết hợp đặc biệt, không cần hoán đổi
            return True
        
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
        
        return True
    
    def shift_candies_down(self):
        """Di chuyển kẹo xuống để lấp đầy khoảng trống"""
        # Đánh dấu tất cả các kẹo đã được xóa
        removed_count = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is not None and self.grid[row][col].remove:
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
                    self.grid[target_row][col] = self.grid[row][col]
                    self.grid[row][col] = None
                    
                    # Cập nhật vị trí của kẹo
                    self.grid[target_row][col].row = target_row
                    self.grid[target_row][col].col = col
                    self.grid[target_row][col].target_y = GRID_OFFSET_Y + target_row * CELL_SIZE
                    self.grid[target_row][col].target_x = GRID_OFFSET_X + col * CELL_SIZE
                    
                    # Thêm vị trí cũ vào danh sách ô trống
                    empty_spaces.append(row)
                    # Sắp xếp lại danh sách ô trống theo thứ tự giảm dần
                    empty_spaces.sort(reverse=True)
        
        # Kiểm tra xem còn ô trống nào không
        empty_count = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    empty_count += 1
        
        print(f"Sau khi di chuyển kẹo xuống, còn {empty_count} ô trống")
    
    def fill_empty_spaces(self):
        """Điền các ô trống với kẹo mới"""
        from candy import Candy
        
        filled_count = 0
        for col in range(GRID_SIZE):
            empty_count = 0
            for row in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    # Tạo kẹo mới
                    candy_type = self.get_random_candy_type(row, col)
                    self.grid[row][col] = Candy(row, col, candy_type)
                    
                    # Đặt vị trí ban đầu cao hơn lưới dựa vào số lượng ô trống
                    empty_count += 1
                    start_y = GRID_OFFSET_Y - empty_count * CELL_SIZE
                    
                    # Đặt vị trí ban đầu và đích
                    self.grid[row][col].x = GRID_OFFSET_X + col * CELL_SIZE
                    self.grid[row][col].y = start_y
                    self.grid[row][col].target_x = GRID_OFFSET_X + col * CELL_SIZE
                    self.grid[row][col].target_y = GRID_OFFSET_Y + row * CELL_SIZE
                    
                    # Đảm bảo kẹo mới không bị đánh dấu để xóa
                    self.grid[row][col].remove = False
                    filled_count += 1
        
        print(f"Đã điền {filled_count} ô trống với kẹo mới")
        
        # Kiểm tra lại sau khi điền
        empty_count = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    empty_count += 1
                    print(f"CẢNH BÁO: Vẫn còn ô trống tại [{row}][{col}] sau khi điền!")
        
        if empty_count > 0:
            print(f"CẢNH BÁO: Vẫn còn {empty_count} ô trống sau khi điền!")
    
    def is_level_complete(self):
        """Kiểm tra xem cấp độ đã hoàn thành chưa"""
        # Cấp độ hoàn thành khi đạt điểm mục tiêu và phá hủy tất cả nút chặn
        return self.score >= self.target_score and self.blockers_count <= 0
    
    def update_candies(self):
        """Cập nhật tất cả kẹo trong lưới"""
        any_moving = False
        
        # Cập nhật vị trí của tất cả kẹo
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

    def add_moves(self, amount):
        """Thêm lượt di chuyển cho cấp độ."""
        self.moves_left += amount
