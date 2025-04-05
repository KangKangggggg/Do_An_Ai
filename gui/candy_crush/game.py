import pygame
import sys
from constants import *
from ui import UI
from levels.level_factory import create_level

class CandyCrushGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Candy Crush")
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)
        
        self.selected_candy = None
        self.swapping_candy = None
        self.game_state = GameState.MENU
        self.level_number = 1
        self.level_type = LevelType.SCORE
        
        # Tạo cấp độ đầu tiên
        self.current_level = create_level(self.level_type, self.level_number)
        self.current_level.initialize()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if self.game_state == GameState.MENU:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.start_level(self.level_number)
            
            elif self.game_state == GameState.PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.handle_click(mouse_pos)
                
                # Phím debug để chuyển loại cấp độ
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.level_type = LevelType.SCORE
                        self.start_level(self.level_number)
                    elif event.key == pygame.K_2:
                        self.level_type = LevelType.JELLY
                        self.start_level(self.level_number)
                    elif event.key == pygame.K_3:
                        self.level_type = LevelType.INGREDIENTS
                        self.start_level(self.level_number)
                    elif event.key == pygame.K_4:
                        self.level_type = LevelType.CHOCOLATE
                        self.start_level(self.level_number)
            
            elif self.game_state in [GameState.GAME_OVER, GameState.LEVEL_COMPLETE]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.game_state == GameState.LEVEL_COMPLETE:
                        self.level_number += 1
                        self.start_level(self.level_number)
                    else:
                        self.start_level(self.level_number)
    
    def start_level(self, level_number):
        """Bắt đầu một cấp độ mới"""
        self.level_number = level_number
        
        # Đặt loại cấp độ dựa trên số cấp độ
        if level_number % 4 == 1:
            self.level_type = LevelType.SCORE
        elif level_number % 4 == 2:
            self.level_type = LevelType.JELLY
        elif level_number % 4 == 3:
            self.level_type = LevelType.INGREDIENTS
        else:
            self.level_type = LevelType.CHOCOLATE
        
        # Tạo và khởi tạo cấp độ
        self.current_level = create_level(self.level_type, level_number)
        self.current_level.initialize()
        
        self.selected_candy = None
        self.swapping_candy = None
        self.game_state = GameState.PLAYING
    
    def handle_click(self, mouse_pos):
        """Xử lý nhấp chuột trên lưới"""
        # Chuyển đổi vị trí chuột thành tọa độ lưới
        col = (mouse_pos[0] - GRID_OFFSET_X) // CELL_SIZE
        row = (mouse_pos[1] - GRID_OFFSET_Y) // CELL_SIZE
        
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            if self.selected_candy is None:
                self.selected_candy = (row, col)
            else:
                # Kiểm tra xem lựa chọn mới có liền kề với lựa chọn trước đó không
                prev_row, prev_col = self.selected_candy
                if ((abs(row - prev_row) == 1 and col == prev_col) or 
                    (abs(col - prev_col) == 1 and row == prev_row)):
                    # Hoán đổi kẹo
                    self.swapping_candy = (row, col)
                    self.current_level.swap_candies(prev_row, prev_col, row, col)
                    self.current_level.moves_left -= 1
                    self.game_state = GameState.SWAPPING
                else:
                    # Chọn kẹo mới
                    self.selected_candy = (row, col)
    
    def update(self):
        """Cập nhật trạng thái trò chơi"""
        # Cập nhật tất cả kẹo
        any_moving = self.current_level.update_candies()
        
        # Máy trạng thái
        if self.game_state == GameState.SWAPPING:
            if not any_moving:
                # Kiểm tra xem việc hoán đổi có tạo ra sự khớp không
                if self.current_level.find_matches():
                    self.game_state = GameState.MATCHING
                else:
                    # Hoán đổi lại nếu không có sự khớp
                    row1, col1 = self.selected_candy
                    row2, col2 = self.swapping_candy
                    self.current_level.swap_candies(row1, col1, row2, col2)
                    self.current_level.moves_left += 1  # Hoàn lại lượt đi
                    self.game_state = GameState.PLAYING
                
                self.selected_candy = None
                self.swapping_candy = None
        
        elif self.game_state == GameState.MATCHING:
            if not any_moving:
                self.current_level.remove_matches()
                self.game_state = GameState.REFILLING
        
        elif self.game_state == GameState.REFILLING:
            if not any_moving:
                # Kiểm tra các sự khớp mới
                if self.current_level.find_matches():
                    self.game_state = GameState.MATCHING
                else:
                    self.game_state = GameState.PLAYING
                    self.selected_candy = None
                    
                    # Kiểm tra điều kiện thắng/thua
                    if self.current_level.moves_left <= 0:
                        if self.current_level.is_level_complete():
                            self.game_state = GameState.LEVEL_COMPLETE
                        else:
                            self.game_state = GameState.GAME_OVER
                    elif self.current_level.is_level_complete():
                        self.game_state = GameState.LEVEL_COMPLETE
    
    def draw(self):
        """Vẽ trò chơi"""
        # Xóa màn hình
        self.screen.fill(WHITE)
        
        # Vẽ lưới
        self.ui.draw_grid()
        
        # Vẽ kẹo
        self.current_level.draw_candies(self.screen)
        
        # Vẽ lựa chọn
        if self.selected_candy is not None:
            row, col = self.selected_candy
            self.ui.draw_selection(row, col)
        
        # Vẽ giao diện người dùng
        if self.level_type == LevelType.SCORE:
            self.ui.draw_level_info(
                self.level_number, 
                self.current_level.score, 
                self.current_level.moves_left, 
                self.level_type,
                target_score=self.current_level.target_score
            )
        elif self.level_type == LevelType.JELLY:
            self.ui.draw_level_info(
                self.level_number, 
                self.current_level.score, 
                self.current_level.moves_left, 
                self.level_type,
                jellies_left=self.current_level.jellies_left
            )
        elif self.level_type == LevelType.INGREDIENTS:
            self.ui.draw_level_info(
                self.level_number, 
                self.current_level.score, 
                self.current_level.moves_left, 
                self.level_type,
                ingredients_left=self.current_level.ingredients_left
            )
        elif self.level_type == LevelType.CHOCOLATE:
            self.ui.draw_level_info(
                self.level_number, 
                self.current_level.score, 
                self.current_level.moves_left, 
                self.level_type,
                chocolates_left=self.current_level.chocolates_left
            )
        
        # Vẽ thông báo trạng thái trò chơi
        if self.game_state == GameState.MENU:
            self.ui.draw_message("Candy Crush", "Nhấn SPACE để bắt đầu")
        elif self.game_state == GameState.GAME_OVER:
            self.ui.draw_message("Kết Thúc", "Nhấn SPACE để thử lại")
        elif self.game_state == GameState.LEVEL_COMPLETE:
            self.ui.draw_message("Hoàn Thành!", "Nhấn SPACE để qua màn tiếp theo")
        
        # Cập nhật màn hình
        pygame.display.flip()
    
    def run(self):
        """Vòng lặp chính của trò chơi"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)