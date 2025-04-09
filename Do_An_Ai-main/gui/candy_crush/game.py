import pygame
import random
import sys
import time
from constants import *
from candy import Candy
from ui import UI

class CandyCrushGame:
    def __init__(self):
        # Khởi tạo màn hình
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Trò Chơi Candy Crush")
        
        # Khởi tạo UI
        self.ui = UI(self.screen)
        
        # Khởi tạo biến trò chơi
        self.state = GameState.MENU  # Bắt đầu với trạng thái MENU
        self.level_number = 1
        self.score = 0
        self.moves_left = 35
        self.level_type = LevelType.SCORE
        self.target_score = 600
        self.jellies_left = 0
        self.ingredients_left = 0
        self.chocolates_left = 0
        self.blockers_count = 0
        
        # Khởi tạo bảng
        self.board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.fill_board()
        
        # Biến cho việc chọn kẹo
        self.selected_row = -1
        self.selected_col = -1
        self.swapping = False
        self.swap_start_time = 0
        self.swap_row1 = -1
        self.swap_col1 = -1
        self.swap_row2 = -1
        self.swap_col2 = -1
        
        # Biến cho hiệu ứng
        self.animations = []
        self.waiting_for_animations = False
        self.animation_start_time = 0
        
        # Đồng hồ
        self.clock = pygame.time.Clock()
    
    def run(self):
        running = True
        while running:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Thêm xử lý phím Space để chuyển cấp độ
                        if self.state == GameState.PLAYING:
                            self.next_level()
                        elif self.state == GameState.MENU:
                            self.state = GameState.PLAYING
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click()
        
            # Cập nhật trạng thái trò chơi
            if self.state == GameState.PLAYING:
                self.update()
        
            # Vẽ trò chơi
            self.draw()
        
            # Cập nhật màn hình
            pygame.display.flip()
        
            # Giới hạn FPS
            self.clock.tick(60)
    
        pygame.quit()
        sys.exit()
    
    def next_level(self):
        """Chuyển sang cấp độ tiếp theo"""
        # Tăng số cấp độ
        self.level_number += 1
        
        # Đặt lại các biến trò chơi
        self.score = 0
        self.moves_left = 35
        
        # Chỉ sử dụng cấp độ điểm để đơn giản hóa
        self.level_type = LevelType.SCORE
        self.jellies_left = 0
        self.ingredients_left = 0
        self.chocolates_left = 0
        
        # Cập nhật mục tiêu điểm
        self.target_score = 600 * self.level_number
        
        # Đặt lại trạng thái trò chơi
        self.state = GameState.PLAYING
        
        # Đặt lại bảng
        self.board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.fill_board()
        
        # Đặt lại biến chọn
        self.selected_row = -1
        self.selected_col = -1
        self.swapping = False
    
    def update(self):
        # Cập nhật các kẹo (di chuyển, hiệu ứng)
        any_moving = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col]:
                    self.board[row][col].update()
                    if self.board[row][col].moving:
                        any_moving = True
        
        # Nếu đang hoán đổi kẹo
        if self.swapping:
            current_time = time.time()
            if current_time - self.swap_start_time > 0.3:  # Thời gian hoán đổi
                self.swapping = False
                # Kiểm tra xem có khớp sau khi hoán đổi không
                matches = self.find_matches()
                if not matches:
                    # Nếu không có khớp, hoán đổi lại
                    self.swap_candies(self.swap_row1, self.swap_col1, self.swap_row2, self.swap_col2)
                else:
                    # Nếu có khớp, xử lý khớp
                    self.process_matches(matches)
                    self.moves_left -= 1
        
        # Nếu không có kẹo nào đang di chuyển và không đang hoán đổi
        if not any_moving and not self.swapping and not self.waiting_for_animations:
            # Kiểm tra và xử lý các kẹo rơi
            if self.handle_falling_candies():
                return
            
            # Kiểm tra các khớp
            matches = self.find_matches()
            if matches:
                self.process_matches(matches)
            
            # Kiểm tra điều kiện kết thúc cấp độ
            self.check_level_completion()
    
    def fill_board(self):
        # Tạo bảng kẹo ban đầu - chỉ sử dụng kẹo thông thường
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                # Tạo kẹo ngẫu nhiên
                candy_type = random.choice(list(CandyType))
                
                # Đảm bảo không tạo ra khớp ngay từ đầu
                attempts = 0
                while attempts < 10 and self.would_create_match(row, col, candy_type):
                    candy_type = random.choice(list(CandyType))
                    attempts += 1
                
                self.board[row][col] = Candy(row, col, candy_type)
    
    def would_create_match(self, row, col, candy_type):
        # Kiểm tra xem việc đặt kẹo có tạo ra khớp không
        # Kiểm tra hàng ngang
        if col >= 2:
            if (self.board[row][col-1] and self.board[row][col-1].candy_type == candy_type and
                self.board[row][col-2] and self.board[row][col-2].candy_type == candy_type):
                return True
        
        # Kiểm tra hàng dọc
        if row >= 2:
            if (self.board[row-1][col] and self.board[row-1][col].candy_type == candy_type and
                self.board[row-2][col] and self.board[row-2][col].candy_type == candy_type):
                return True
        
        return False
    
    def handle_mouse_click(self):
        # Xử lý sự kiện click chuột
        mouse_pos = pygame.mouse.get_pos()
        
        # Kiểm tra xem có click vào nút play không
        if self.ui.play_button_rect.collidepoint(mouse_pos):
            if self.state == GameState.MENU:
                # Bắt đầu trò chơi nếu đang ở màn hình menu
                self.state = GameState.PLAYING
                # Đặt lại các biến trò chơi khi bắt đầu mới
                self.level_number = 1
                self.score = 0
                self.moves_left = 35
                self.target_score = 600
                # Đặt lại bảng
                self.board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
                self.fill_board()
            elif self.state == GameState.LEVEL_COMPLETE or self.state == GameState.GAME_OVER:
                # Bắt đầu cấp độ mới nếu đã hoàn thành hoặc thua
                self.next_level()
            return
        
        # Kiểm tra xem có click vào nút cài đặt không
        if self.ui.settings_rect.collidepoint(mouse_pos):
            # Xử lý khi click vào nút cài đặt (có thể thêm sau)
            print("Settings button clicked")
            return
        
        # Chỉ xử lý click vào lưới nếu đang trong trạng thái PLAYING
        if self.state == GameState.PLAYING:
            # Chuyển đổi vị trí chuột thành tọa độ lưới
            col = (mouse_pos[0] - GRID_OFFSET_X) // CELL_SIZE
            row = (mouse_pos[1] - GRID_OFFSET_Y) // CELL_SIZE
        
            # Kiểm tra xem click có nằm trong lưới không
            if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                # Nếu chưa có ô nào được chọn
                if self.selected_row == -1 and self.selected_col == -1:
                    self.selected_row = row
                    self.selected_col = col
                else:
                    # Nếu đã có ô được chọn, kiểm tra xem ô mới có kề với ô đã chọn không
                    if ((abs(row - self.selected_row) == 1 and col == self.selected_col) or
                        (abs(col - self.selected_col) == 1 and row == self.selected_row)):
                        # Hoán đổi hai kẹo
                        self.swap_candies(self.selected_row, self.selected_col, row, col)
                        self.swap_row1 = self.selected_row
                        self.swap_col1 = self.selected_col
                        self.swap_row2 = row
                        self.swap_col2 = col
                        self.swapping = True
                        self.swap_start_time = time.time()
                    
                    # Bỏ chọn ô hiện tại
                    self.selected_row = -1
                    self.selected_col = -1
    
    def swap_candies(self, row1, col1, row2, col2):
        # Hoán đổi hai kẹo
        candy1 = self.board[row1][col1]
        candy2 = self.board[row2][col2]
        
        # Cập nhật vị trí trong lưới
        self.board[row1][col1] = candy2
        self.board[row2][col2] = candy1
        
        if candy1:
            candy1.row = row2
            candy1.col = col2
            candy1.target_x = GRID_OFFSET_X + col2 * CELL_SIZE
            candy1.target_y = GRID_OFFSET_Y + row2 * CELL_SIZE
        
        if candy2:
            candy2.row = row1
            candy2.col = col1
            candy2.target_x = GRID_OFFSET_X + col1 * CELL_SIZE
            candy2.target_y = GRID_OFFSET_Y + row1 * CELL_SIZE
    
    def find_matches(self):
        matches = []
        
        # Tìm khớp hàng ngang
        for row in range(GRID_SIZE):
            col = 0
            while col < GRID_SIZE - 2:
                if (self.board[row][col] and not self.board[row][col].remove and
                    self.board[row][col+1] and not self.board[row][col+1].remove and
                    self.board[row][col+2] and not self.board[row][col+2].remove and
                    self.board[row][col].candy_type == self.board[row][col+1].candy_type and
                    self.board[row][col].candy_type == self.board[row][col+2].candy_type):
                    
                    # Tìm độ dài của khớp
                    match_length = 3
                    while col + match_length < GRID_SIZE and self.board[row][col+match_length] and self.board[row][col].candy_type == self.board[row][col+match_length].candy_type:
                        match_length += 1
                    
                    # Thêm khớp vào danh sách
                    match = {'type': 'horizontal', 'row': row, 'col': col, 'length': match_length, 'candy_type': self.board[row][col].candy_type}
                    matches.append(match)
                    
                    col += match_length
                else:
                    col += 1
        
        # Tìm khớp hàng dọc
        for col in range(GRID_SIZE):
            row = 0
            while row < GRID_SIZE - 2:
                if (self.board[row][col] and not self.board[row][col].remove and
                    self.board[row+1][col] and not self.board[row+1][col].remove and
                    self.board[row+2][col] and not self.board[row+2][col].remove and
                    self.board[row][col].candy_type == self.board[row+1][col].candy_type and
                    self.board[row][col].candy_type == self.board[row+2][col].candy_type):
                    
                    # Tìm độ dài của khớp
                    match_length = 3
                    while row + match_length < GRID_SIZE and self.board[row+match_length][col] and self.board[row][col].candy_type == self.board[row+match_length][col].candy_type:
                        match_length += 1
                    
                    # Thêm khớp vào danh sách
                    match = {'type': 'vertical', 'row': row, 'col': col, 'length': match_length, 'candy_type': self.board[row][col].candy_type}
                    matches.append(match)
                    
                    row += match_length
                else:
                    row += 1
        
        return matches
    
    def process_matches(self, matches):
        # Xử lý các khớp
        for match in matches:
            # Tính điểm
            match_score = match['length'] * 10
            self.score += match_score
            
            # Xác định loại kẹo đặc biệt sẽ tạo ra
            special_type = SpecialType.NORMAL
            special_row = -1
            special_col = -1
            
            if match['length'] >= 5:
                special_type = SpecialType.COLOR_BOMB
                special_row = match['row'] if match['type'] == 'horizontal' else match['row']
                special_col = match['col'] if match['type'] == 'vertical' else match['col']
            elif match['length'] == 4:
                special_type = SpecialType.STRIPED_H if match['type'] == 'horizontal' else SpecialType.STRIPED_V
                special_row = match['row']
                special_col = match['col']
            elif match['length'] == 3 and len(matches) > 1:
                # Tìm giao điểm của hai khớp để tạo kẹo bọc
                for other_match in matches:
                    if other_match != match:
                        if match['type'] == 'horizontal' and other_match['type'] == 'vertical':
                            for c in range(match['col'], match['col'] + match['length']):
                                if c == other_match['col'] and match['row'] >= other_match['row'] and match['row'] < other_match['row'] + other_match['length']:
                                    special_type = SpecialType.WRAPPED
                                    special_row = match['row']
                                    special_col = c
                                    break
                        elif match['type'] == 'vertical' and other_match['type'] == 'horizontal':
                            for r in range(match['row'], match['row'] + match['length']):
                                if r == other_match['row'] and match['col'] >= other_match['col'] and match['col'] < other_match['col'] + other_match['length']:
                                    special_type = SpecialType.WRAPPED
                                    special_row = r
                                    special_col = match['col']
                                    break
            
            # Đánh dấu các kẹo để xóa
            if match['type'] == 'horizontal':
                for c in range(match['col'], match['col'] + match['length']):
                    if self.board[match['row']][c]:
                        self.board[match['row']][c].remove = True
            
            elif match['type'] == 'vertical':
                for r in range(match['row'], match['row'] + match['length']):
                    if self.board[r][match['col']]:
                        self.board[r][match['col']].remove = True
        
        # Xóa các kẹo đã khớp và tạo kẹo đặc biệt
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] and self.board[row][col].remove:
                    # Tạo kẹo đặc biệt nếu cần
                    if special_row == row and special_col == col and special_type != SpecialType.NORMAL:
                        self.board[row][col].remove = False
                        self.board[row][col].special_type = special_type
                    else:
                        self.board[row][col] = None
    
    def handle_falling_candies(self):
        # Xử lý các kẹo rơi
        candies_moved = False
        
        # Di chuyển các kẹo xuống dưới
        for col in range(GRID_SIZE):
            # Đếm số ô trống trong cột
            empty_spaces = 0
            for row in range(GRID_SIZE - 1, -1, -1):
                if not self.board[row][col]:
                    empty_spaces += 1
                elif empty_spaces > 0:
                    # Di chuyển kẹo xuống
                    self.board[row + empty_spaces][col] = self.board[row][col]
                    self.board[row][col] = None
                    
                    # Cập nhật vị trí của kẹo
                    self.board[row + empty_spaces][col].row = row + empty_spaces
                    self.board[row + empty_spaces][col].target_y = GRID_OFFSET_Y + (row + empty_spaces) * CELL_SIZE
                    
                    candies_moved = True
        
        # Tạo kẹo mới ở trên cùng
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE):
                if not self.board[row][col]:
                    # Tạo kẹo mới
                    candy_type = random.choice(list(CandyType))
                    self.board[row][col] = Candy(row, col, candy_type)
                    
                    # Đặt vị trí ban đầu ở trên màn hình
                    self.board[row][col].y = GRID_OFFSET_Y - CELL_SIZE
                    self.board[row][col].target_y = GRID_OFFSET_Y + row * CELL_SIZE
                    
                    candies_moved = True
        
        return candies_moved
    
    def draw(self):
        # Vẽ nền
        self.screen.fill(WHITE)
        
        # Cập nhật trạng thái game cho UI
        self.ui.game_state = self.state
        
        if self.state == GameState.MENU:
            # Vẽ màn hình menu
            self.ui.draw_menu()
        else:
            # Vẽ lưới
            self.ui.draw_grid()
        
            # Vẽ các kẹo
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.board[row][col]:
                        self.board[row][col].draw(self.screen)
        
            # Vẽ ô được chọn
            if self.selected_row >= 0 and self.selected_col >= 0:
                self.ui.draw_selection(self.selected_row, self.selected_col)
        
            # Vẽ thông tin cấp độ
            self.ui.draw_level_info(
                self.level_number, 
                self.score, 
                self.moves_left, 
                self.level_type, 
                self.target_score,
                self.jellies_left,
                self.ingredients_left,
                self.chocolates_left,
                self.blockers_count
            )
        
            # Vẽ thông báo khi kết thúc trò chơi
            if self.state == GameState.GAME_OVER:
                self.ui.draw_message("Trò Chơi Kết Thúc", "Nhấn SPACE để chơi cấp độ tiếp theo hoặc ESC để thoát")
            elif self.state == GameState.LEVEL_COMPLETE:
                self.ui.draw_message("Hoàn Thành Cấp Độ!", "Nhấn SPACE để chơi cấp độ tiếp theo hoặc ESC để thoát")
    
    def check_level_completion(self):
        # Kiểm tra điều kiện hoàn thành cấp độ
        if self.moves_left <= 0:
            if self.score >= self.target_score:
                self.state = GameState.LEVEL_COMPLETE
            else:
                self.state = GameState.GAME_OVER
        elif self.score >= self.target_score:
            self.state = GameState.LEVEL_COMPLETE
