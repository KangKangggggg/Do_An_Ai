import pygame
import random
import sys
import time
import os
from constants import *
from candy import Candy
from ui import UI
import pygame.mixer
import math
from algorithms import AIAlgorithms
from constants import CANDY_COLORS
from levels import create_level

class CandyCrushGame:
    def __init__(self):
        # Khởi tạo pygame và màn hình
        pygame.init()
        
        # Khởi tạo màn hình
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Trò Chơi Candy Crush với AI")
        
        # Khởi tạo âm thanh
        try:
            pygame.mixer.init()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(script_dir, "assets")
            os.makedirs(assets_dir, exist_ok=True)
            
            sound_files = ["pop.wav", "swap.wav", "match.wav", "level_complete.wav"]
            for sound_file in sound_files:
                sound_path = os.path.join(assets_dir, sound_file)
                if not os.path.exists(sound_path):
                    with open(sound_path, 'wb') as f:
                        f.write(b'RIFF')
                        f.write((36).to_bytes(4, 'little'))
                        f.write(b'WAVE')
                        f.write(b'fmt ')
                        f.write((16).to_bytes(4, 'little'))
                        f.write((1).to_bytes(2, 'little'))
                        f.write((1).to_bytes(2, 'little'))
                        f.write((8000).to_bytes(4, 'little'))
                        f.write((8000).to_bytes(4, 'little'))
                        f.write((1).to_bytes(2, 'little'))
                        f.write((8).to_bytes(2, 'little'))
                        f.write(b'data')
                        f.write((0).to_bytes(4, 'little'))
            
            self.pop_sound = pygame.mixer.Sound(os.path.join(assets_dir, "pop.wav"))
            self.swap_sound = pygame.mixer.Sound(os.path.join(assets_dir, "swap.wav"))
            self.match_sound = pygame.mixer.Sound(os.path.join(assets_dir, "match.wav"))
            self.level_complete_sound = pygame.mixer.Sound(os.path.join(assets_dir, "level_complete.wav"))
            
        except Exception as e:
            print(f"Không thể khởi tạo hệ thống âm thanh: {str(e)}")
            class DummySound:
                def play(self):
                    pass
            self.pop_sound = DummySound()
            self.swap_sound = DummySound()
            self.match_sound = DummySound()
            self.level_complete_sound = DummySound()
            class DummyMusic:
                @staticmethod
                def set_volume(vol):
                    pass
                @staticmethod
                def play(loops=0):
                    pass
                @staticmethod
                def stop():
                    pass
            pygame.mixer.music = DummyMusic()
        
        # Khởi tạo UI
        self.ui = UI(self.screen)
        
        # Định nghĩa các cấp độ - Thay đổi level 3 thành cấp độ điểm đơn giản
        self.levels = [
            {"target_score": 500, "moves_left": 20, "level_type": LevelType.SCORE},
            {"target_score": 800, "moves_left": 30, "level_type": LevelType.JELLY},
            {"target_score": 900, "moves_left": 35, "level_type": LevelType.SCORE},  # Đổi từ CHOCOLATE thành SCORE
            {"target_score": 1500, "moves_left": 35, "level_type": LevelType.SCORE},
        ]
        self.current_level = 0
        self.unlocked_levels = 0
        self.state = GameState.MENU
        
        # Khởi tạo cấp độ
        self.level = None
        self.initialize_level()
        
        # Biến cho việc chọn và di chuyển kẹo
        self.selected_candy = None
        self.dragging = False
        self.drag_start_pos = None
        self.swapping = False
        self.swap_start_time = 0
        self.swap_row1 = -1
        self.swap_col1 = -1
        self.swap_row2 = -1
        self.swap_col2 = -1
        self.swap_animation_duration = 0.2  # Giảm thời gian hoạt hình để mượt hơn
        self.swap_back_animation = False
        
        # Biến cho hoạt hình và hiệu ứng
        self.animations = []
        self.waiting_for_animations = False
        self.animation_start_time = 0
        self.effects = []
        
        # Đồng hồ trò chơi
        self.clock = pygame.time.Clock()
        
        # Cài đặt
        self.settings = {
            "volume": 1.0,
            "vibration": True,
            "music": True,
            "ai_mode": False,
            "ai_algorithm": "hybrid",
            "free_movement": False,
            "auto_play": False
        }
        
        # Biến cho chế độ tự động chơi
        self.auto_play_timer = 0
        self.auto_play_interval = 0.8  # Giảm thời gian chờ để mượt hơn
        
        # Khởi tạo AI
        self.ai = AIAlgorithms(self)

        # Biến cho chức năng so sánh thuật toán
        self.comparing_algorithms = False
        self.algorithm1 = None
        self.algorithm2 = None
        self.algorithm1_score = 0
        self.algorithm2_score = 0
        self.algorithm1_moves = []
        self.algorithm2_moves = []
        self.comparison_results = None
        
        # Biến cho nước đi không hợp lệ
        self.hint_move = None
        self.show_hint = False
        
        # Biến cho nước đi không hợp lệ
        self.invalid_move = False
        self.invalid_move_time = 0
        self.invalid_move_duration = 0.3  # Giảm thời gian hiển thị hiệu ứng
        self.invalid_move_positions = None
            
    def run(self):
        """Chạy vòng lặp chính của trò chơi."""
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event.pos)
            
            # Cập nhật trạng thái trò chơi
            self.update()
            
            # Vẽ màn hình
            self.draw()
            pygame.display.flip()
            
            # Giới hạn tốc độ khung hình
            clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def force_candies_to_grid_positions(self):
        """Đặt tất cả kẹo vào đúng vị trí lưới của chúng"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] is not None:
                    self.board[row][col].x = GRID_OFFSET_X + col * CELL_SIZE
                    self.board[row][col].y = GRID_OFFSET_Y + row * CELL_SIZE
                    self.board[row][col].target_x = self.board[row][col].x
                    self.board[row][col].target_y = self.board[row][col].y
                    self.board[row][col].moving = False
    
    def initialize_level(self):
        level_info = self.levels[self.current_level]
        level_type = level_info["level_type"]
        self.level = create_level(level_type, self.current_level + 1)
        self.level.moves_left = level_info["moves_left"]  # Make sure this line is working
        self.level.target_score = level_info["target_score"]  # Đảm bảo target_score được cập nhật
        self.level.initialize()
        
        self.board = self.level.grid
        self.score = self.level.score
        self.moves_left = self.level.moves_left
        self.target_score = self.level.target_score
        self.level_type = self.level.level_type
        self.jellies_left = getattr(self.level, 'jellies_left', 0)
        self.ingredients_left = getattr(self.level, 'ingredients_left', 0)
        self.chocolates_left = getattr(self.level, 'chocolates_left', 0)
        self.blockers_count = self.level.blockers_count
        
        self.force_candies_to_grid_positions()
        
        # Debug information about the level
        print(f"Initialized level {self.current_level + 1}")
        print(f"Level type: {self.level_type.name}")
        print(f"Moves left: {self.level.moves_left}")
        print(f"Target score: {self.level.target_score}")
        
        if self.level_type == LevelType.JELLY:
            print(f"Jellies left: {self.level.jellies_left}")
        elif self.level_type == LevelType.INGREDIENT:
            print(f"Ingredients left: {self.level.ingredients_left}")
        elif self.level_type == LevelType.CHOCOLATE:
            print(f"Chocolates left: {self.level.chocolates_left}")
    
    def reset_level(self):
        self.initialize_level()
        self.selected_candy = None  # Đặt lại lựa chọn khi reset level
    
    def toggle_ai_mode(self):
        self.settings["ai_mode"] = not self.settings["ai_mode"]
        if self.settings["ai_mode"]:
            self.settings["auto_play"] = False
    
    def toggle_free_movement(self):
        self.settings["free_movement"] = not self.settings["free_movement"]
        self.selected_candy = None
        self.dragging = False
    
    def toggle_auto_play(self):
        self.settings["auto_play"] = not self.settings["auto_play"]
        if self.settings["auto_play"]:
            self.settings["ai_mode"] = False
            self.auto_play_timer = time.time()
    
    def get_hint(self):
        self.hint_move = self.ai.get_best_move(
            algorithm=self.settings["ai_algorithm"],
            max_depth=2,
            iterations=5
        )
        self.show_hint = True

    def compare_algorithms(self, algorithm1, algorithm2):
        """So sánh hiệu suất của hai thuật toán"""
        # Kiểm tra xem có đủ thuật toán để so sánh không
        available_algorithms = self.ui.algorithm_values.copy()
        if len(available_algorithms) < 2:
            print("Cần ít nhất 2 thuật toán để so sánh")
            self.ui.show_message("Cần ít nhất 2 thuật toán để so sánh", 2000)
            return None
            
        self.comparing_algorithms = True
        self.algorithm1 = algorithm1
        self.algorithm2 = algorithm2
        self.algorithm1_score = 0
        self.algorithm2_score = 0
        self.algorithm1_moves = []
        self.algorithm2_moves = []
        
        # Số lượt thử nghiệm
        test_runs = 5
        
        print(f"Bắt đầu so sánh thuật toán {algorithm1} và {algorithm2}...")
        
        # Thực hiện nhiều lượt thử nghiệm
        for i in range(test_runs):
            # Lấy nước đi từ thuật toán 1
            move1 = self.ai.get_best_move(algorithm=algorithm1, max_depth=2, iterations=5)
            if move1:
                row1, col1, row2, col2 = move1
                # Đánh giá nước đi
                score1 = self.ai.evaluate_move(move1)
                self.algorithm1_score += score1
                self.algorithm1_moves.append((move1, score1))
                print(f"Thuật toán {algorithm1} - Nước đi: {move1}, Điểm: {score1}")
            
            # Lấy nước đi từ thuật toán 2
            move2 = self.ai.get_best_move(algorithm=algorithm2, max_depth=2, iterations=5)
            if move2:
                row1, col1, row2, col2 = move2
                # Đánh giá nước đi
                score2 = self.ai.evaluate_move(move2)
                self.algorithm2_score += score2
                self.algorithm2_moves.append((move2, score2))
                print(f"Thuật toán {algorithm2} - Nước đi: {move2}, Điểm: {score2}")
        
        # Tính điểm trung bình
        avg_score1 = self.algorithm1_score / test_runs if test_runs > 0 else 0
        avg_score2 = self.algorithm2_score / test_runs if test_runs > 0 else 0
        
        # Xác định thuật toán tốt hơn
        if avg_score1 > avg_score2:
            better_algorithm = algorithm1
            score_diff = avg_score1 - avg_score2
        else:
            better_algorithm = algorithm2
            score_diff = avg_score2 - avg_score1
        
        # Lưu kết quả so sánh
        self.comparison_results = {
            "algorithm1": algorithm1,
            "algorithm2": algorithm2,
            "avg_score1": avg_score1,
            "avg_score2": avg_score2,
            "better_algorithm": better_algorithm,
            "score_diff": score_diff
        }
        
        print(f"Kết quả so sánh: {self.comparison_results}")
        self.comparing_algorithms = False
        
        return self.comparison_results

    def draw_comparison_results(self):
        """Hiển thị kết quả so sánh thuật toán"""
        if not self.comparison_results:
            return
        
        # Tạo overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Tạo panel kết quả
        panel_width = 500
        panel_height = 300
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        pygame.draw.rect(self.screen, (240, 240, 240), 
                         (panel_x, panel_y, panel_width, panel_height), 
                         border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), 
                         (panel_x, panel_y, panel_width, panel_height), 
                         2, border_radius=10)
        
        # Tiêu đề
        title_font = pygame.font.SysFont(None, 36)
        title = title_font.render("Kết quả so sánh thuật toán", True, (0, 0, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 30))
        self.screen.blit(title, title_rect)
        
        # Thông tin thuật toán 1
        algo1_name = self.comparison_results["algorithm1"]
        algo1_score = self.comparison_results["avg_score1"]
        algo1_text = f"{algo1_name}: {algo1_score:.1f} điểm"
        algo1_font = pygame.font.SysFont(None, 28)
        algo1_surface = algo1_font.render(algo1_text, True, (0, 0, 0))
        self.screen.blit(algo1_surface, (panel_x + 50, panel_y + 80))
        
        # Thông tin thuật toán 2
        algo2_name = self.comparison_results["algorithm2"]
        algo2_score = self.comparison_results["avg_score2"]
        algo2_text = f"{algo2_name}: {algo2_score:.1f} điểm"
        algo2_font = pygame.font.SysFont(None, 28)
        algo2_surface = algo2_font.render(algo2_text, True, (0, 0, 0))
        self.screen.blit(algo2_surface, (panel_x + 50, panel_y + 120))
        
        # Thuật toán tốt hơn
        better_algo = self.comparison_results["better_algorithm"]
        score_diff = self.comparison_results["score_diff"]
        result_text = f"Thuật toán tốt hơn: {better_algo}"
        result_font = pygame.font.SysFont(None, 32)
        result_surface = result_font.render(result_text, True, (0, 100, 0))
        self.screen.blit(result_surface, (panel_x + 50, panel_y + 170))
        
        diff_text = f"Chênh lệch điểm: {score_diff:.1f}"
        diff_font = pygame.font.SysFont(None, 28)
        diff_surface = diff_font.render(diff_text, True, (0, 0, 0))
        self.screen.blit(diff_surface, (panel_x + 50, panel_y + 210))
        
        # Nút đóng
        close_button = pygame.Surface((100, 40))
        close_button.fill((200, 100, 100))
        close_button_rect = close_button.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height - 30))
        self.screen.blit(close_button, close_button_rect)
        
        close_text = pygame.font.SysFont(None, 28).render("Đóng", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=close_button_rect.center)
        self.screen.blit(close_text, close_text_rect)
        
        # Lưu rect của nút đóng để xử lý sự kiện
        self.close_comparison_button_rect = close_button_rect
    
    def make_ai_move(self):
        if not self.swapping and not self.waiting_for_animations:
            best_move = self.ai.get_best_move(
                algorithm=self.settings["ai_algorithm"],
                max_depth=2,
                iterations=5
            )
            if best_move:
                row1, col1, row2, col2 = best_move
                success = self.try_swap_candies(row1, col1, row2, col2)
                if success:
                    self.level.moves_left -= 1
    
    def auto_play_move(self):
        current_time = time.time()
        if current_time - self.auto_play_timer >= self.auto_play_interval:
            self.make_ai_move()
            self.auto_play_timer = current_time
    
    def draw_hint(self):
        if self.show_hint and self.hint_move:
            row1, col1, row2, col2 = self.hint_move
            x1 = GRID_OFFSET_X + col1 * CELL_SIZE + CELL_SIZE // 2
            y1 = GRID_OFFSET_Y + row1 * CELL_SIZE + CELL_SIZE // 2
            x2 = GRID_OFFSET_X + col2 * CELL_SIZE + CELL_SIZE // 2
            y2 = GRID_OFFSET_Y + row2 * CELL_SIZE + CELL_SIZE // 2
            
            pygame.draw.line(self.screen, (255, 255, 0), (x1, y1), (x2, y2), 3)
            angle = math.atan2(y2 - y1, x2 - x1)
            arrow_size = 10
            pygame.draw.polygon(self.screen, (255, 255, 0), [
                (x2, y2),
                (x2 - arrow_size * math.cos(angle - math.pi/6), y2 - arrow_size * math.sin(angle - math.pi/6)),
                (x2 - arrow_size * math.cos(angle + math.pi/6), y2 - arrow_size * math.sin(angle + math.pi/6))
            ])
    
    def update(self):
        if self.state == GameState.PLAYING:
            current_time = time.time()
            
            # Xử lý hoạt hình hoán đổi
            if self.swapping:
                elapsed_time = current_time - self.swap_start_time
                if elapsed_time >= self.swap_animation_duration:
                    self.swapping = False
                    if self.swap_back_animation:
                        self.swap_back_animation = False
                        if self.board[self.swap_row1][self.swap_col1]:
                            self.board[self.swap_row1][self.swap_col1].x = GRID_OFFSET_X + self.swap_col1 * CELL_SIZE
                            self.board[self.swap_row1][self.swap_col1].y = GRID_OFFSET_Y + self.swap_row1 * CELL_SIZE
                            self.board[self.swap_row1][self.swap_col1].target_x = self.board[self.swap_row1][self.swap_col1].x
                            self.board[self.swap_row1][self.swap_col1].target_y = self.board[self.swap_row1][self.swap_col1].y
                        if self.board[self.swap_row2][self.swap_col2]:
                            self.board[self.swap_row2][self.swap_col2].x = GRID_OFFSET_X + self.swap_col2 * CELL_SIZE
                            self.board[self.swap_row2][self.swap_col2].y = GRID_OFFSET_Y + self.swap_row2 * CELL_SIZE
                            self.board[self.swap_row2][self.swap_col2].target_x = self.board[self.swap_row2][self.swap_col2].x
                            self.board[self.swap_row2][self.swap_col2].target_y = self.board[self.swap_row2][self.swap_col2].y
            
            # Xử lý hiệu ứng nước đi không hợp lệ
            if self.invalid_move:
                elapsed_time = current_time - self.invalid_move_time
                if elapsed_time >= self.invalid_move_duration:
                    self.invalid_move = False
                    self.invalid_move_positions = None
            
            # Cập nhật vị trí kẹo
            any_moving = False
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.board[row][col]:
                        self.board[row][col].update()
                        if self.board[row][col].moving:
                            any_moving = True
            
            self.waiting_for_animations = any_moving or self.swapping
            
            # Xử lý logic khi không có hoạt hình
            if not self.waiting_for_animations:
                has_empty = any(self.board[row][col] is None for row in range(GRID_SIZE) for col in range(GRID_SIZE))
                if has_empty:
                    self.check_and_fill_board()
                    self.waiting_for_animations = True
                else:
                    if self.level.find_matches():
                        self.level.remove_matches()
                        self.waiting_for_animations = True
                    else:
                        empty_count = sum(1 for row in range(GRID_SIZE) for col in range(GRID_SIZE) if self.board[row][col] is None)
                        if empty_count > 0:
                            self.level.fill_empty_spaces()
                            self.waiting_for_animations = True
            
            # Xử lý kẹo bọc
            if hasattr(self.level, 'wrapped_explosion_pending') and self.level.wrapped_explosion_pending:
                for row, col in self.level.wrapped_explosion_pending[:]:
                    if (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and 
                        self.board[row][col] is not None and 
                        self.board[row][col].special_type == SpecialType.WRAPPED):
                        self.level.explode_wrapped_candy(row, col, is_second_explosion=True)
                        self.board[row][col].remove = True
                self.level.wrapped_explosion_pending = []
            
            # Kiểm tra hoàn thành cấp độ
            if self.level.is_level_complete():
                print(f"Level {self.current_level + 1} complete! Score: {self.level.score}")
                if self.level_type == LevelType.JELLY:
                    print(f"Jellies left: {self.level.jellies_left}")
                elif self.level_type == LevelType.CHOCOLATE:
                    print(f"Chocolates left: {self.level.chocolates_left}")
                self.state = GameState.LEVEL_COMPLETE
                self.level_complete_sound.play()
            elif self.level.moves_left <= 0 and not self.level.is_level_complete():
                print(f"Game over! Level {self.current_level + 1} failed. Score: {self.level.score}")
                if self.level_type == LevelType.JELLY:
                    print(f"Jellies left: {self.level.jellies_left}")
                elif self.level_type == LevelType.CHOCOLATE:
                    print(f"Chocolates left: {self.level.chocolates_left}")
                self.state = GameState.GAME_OVER
            
            # Xử lý AI và auto play
            if self.settings["ai_mode"] and not self.waiting_for_animations:
                self.make_ai_move()
            if self.settings["auto_play"] and not self.waiting_for_animations:
                self.auto_play_move()
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        if self.state == GameState.MENU:
            self.screen.blit(self.ui.background_image, (0, 0))
            title = self.ui.title_font.render("Candy Crush", True, WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(title, title_rect)
            self.screen.blit(self.ui.play_button, self.ui.play_button_rect)
            play_text = self.ui.font.render("", True, BLACK)
            play_text_rect = play_text.get_rect(center=self.ui.play_button_rect.center)
            self.screen.blit(play_text, play_text_rect)
            self.screen.blit(self.ui.settings_icon, self.ui.settings_rect)
        
        elif self.state == GameState.LEVEL_SELECT:
            self.ui.draw_level_select(self.levels, self.current_level, self.unlocked_levels)
        
        elif self.state == GameState.PLAYING:
            self.ui.draw_level_info(
                self.current_level + 1,
                self.level.score,
                self.level.moves_left,
                self.level.level_type,
                self.level.target_score,
                getattr(self.level, 'jellies_left', 0),
                getattr(self.level, 'ingredients_left', 0),
                getattr(self.level, 'chocolates_left', 0),
                self.level.blockers_count,
                self.settings
            )
            self.level.draw_candies(self.screen)
            
            # Chỉ vẽ khung vàng khi không có hoạt hình và có kẹo được chọn
            if self.selected_candy and not self.dragging and not self.swapping and not self.waiting_for_animations:
                row, col = self.selected_candy
                rect = pygame.Rect(
                    GRID_OFFSET_X + col * CELL_SIZE, 
                    GRID_OFFSET_Y + row * CELL_SIZE, 
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)
            
            # Vẽ kẹo khi kéo
            if self.dragging and self.selected_candy:
                row, col = self.selected_candy
                mouse_pos = pygame.mouse.get_pos()
                candy_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                candy_surface.fill((0, 0, 0, 0))
                candy = self.board[row][col]
                if candy:
                    orig_x, orig_y = candy.x, candy.y
                    candy.x, candy.y = 0, 0
                    candy.draw(candy_surface)
                    candy.x, candy.y = orig_x, orig_y
                self.screen.blit(candy_surface, (mouse_pos[0] - CELL_SIZE // 2, mouse_pos[1] - CELL_SIZE // 2))
            
            if self.show_hint:
                self.draw_hint()
            
            if self.invalid_move and self.invalid_move_positions:
                row1, col1, row2, col2 = self.invalid_move_positions
                rect1 = pygame.Rect(GRID_OFFSET_X + col1 * CELL_SIZE, GRID_OFFSET_Y + row1 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                rect2 = pygame.Rect(GRID_OFFSET_X + col2 * CELL_SIZE, GRID_OFFSET_Y + row2 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, (255, 0, 0), rect1, 3)
                pygame.draw.rect(self.screen, (255, 0, 0), rect2, 3)
        
        if self.state == GameState.SETTINGS:
            self.ui.draw_settings(self.settings)
        
        if self.state in (GameState.GAME_OVER, GameState.LEVEL_COMPLETE):
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            font = pygame.font.SysFont(None, 72)
            text = font.render("Game Over!" if self.state == GameState.GAME_OVER else "Level Complete!", True, (255, 0, 0) if self.state == GameState.GAME_OVER else (0, 255, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(text, text_rect)
            score_font = pygame.font.SysFont(None, 48)
            score_text = score_font.render(f"Score: {self.level.score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(score_text, score_rect)
            self.screen.blit(self.ui.play_button, self.ui.play_button_rect)
            button_font = pygame.font.SysFont(None, 36)
            button_text = button_font.render("Try Again" if self.state == GameState.GAME_OVER else "Next Level", True, (0, 0, 0))
            button_text_rect = button_text.get_rect(center=self.ui.play_button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
        # Hiển thị kết quả so sánh thuật toán nếu có
        if self.comparison_results:
            self.draw_comparison_results()
    
    def get_grid_position(self, mouse_pos):
        if (GRID_OFFSET_X <= mouse_pos[0] <= GRID_OFFSET_X + GRID_SIZE * CELL_SIZE and
            GRID_OFFSET_Y <= mouse_pos[1] <= GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE):
            col = (mouse_pos[0] - GRID_OFFSET_X) // CELL_SIZE
            row = (mouse_pos[1] - GRID_OFFSET_Y) // CELL_SIZE
            return row, col
        return None
    
    def try_swap_candies(self, row1, col1, row2, col2):
        """
        Attempt to swap two candies and check if it creates a match
        
        Args:
            row1, col1: Position of the first candy
            row2, col2: Position of the second candy
            
        Returns:
            bool: True if the swap was successful and created a match
        """
        # Check if the positions are valid
        if not (0 <= row1 < GRID_SIZE and 0 <= col1 < GRID_SIZE and 
                0 <= row2 < GRID_SIZE and 0 <= col2 < GRID_SIZE):
            return False
        
        # Check if the candies are adjacent
        if abs(row1 - row2) + abs(col1 - col2) != 1:
            return False
        
        # Check if either candy has a blocker that prevents swapping
        if (self.board[row1][col1] is None or self.board[row2][col2] is None or
            self.board[row1][col1].blocker_type in [BlockerType.STONE, BlockerType.LOCK, BlockerType.LICORICE] or
            self.board[row2][col2].blocker_type in [BlockerType.STONE, BlockerType.LOCK, BlockerType.LICORICE]):
            # Show invalid move animation
            self.invalid_move = True
            self.invalid_move_time = time.time()
            self.invalid_move_positions = (row1, col1, row2, col2)
            return False
        
        # Check for special candy combinations
        if self.level.check_special_combination(row1, col1, row2, col2):
            self.swap_sound.play()
            self.swapping = True
            self.swap_start_time = time.time()
            self.swap_row1, self.swap_col1 = row1, col1
            self.swap_row2, self.swap_col2 = row2, col2
            return True
        
        # Perform the swap
        self.level.swap_candies(row1, col1, row2, col2)
        
        # Start swap animation
        self.swapping = True
        self.swap_start_time = time.time()
        self.swap_row1, self.swap_col1 = row1, col1
        self.swap_row2, self.swap_col2 = row2, col2
        self.swap_sound.play()
        
        # Check if the swap creates a match
        if self.level.find_matches():
            # Valid move - matches found
            self.match_sound.play()
            return True
        else:
            # Invalid move - no matches, swap back
            self.swap_back_animation = True
            self.level.swap_candies(row1, col1, row2, col2)  # Swap back in the data
            
            # Show invalid move animation
            self.invalid_move = True
            self.invalid_move_time = time.time()
            self.invalid_move_positions = (row1, col1, row2, col2)
            return False

    def handle_mouse_down(self, pos):
        """Xử lý sự kiện nhấn chuột"""
        if self.state == GameState.MENU:
            if self.ui.play_button_rect.collidepoint(pos):
                self.state = GameState.LEVEL_SELECT
            elif self.ui.settings_rect.collidepoint(pos):
                self.state = GameState.SETTINGS
        
        elif self.state == GameState.LEVEL_SELECT:
            if self.ui.home_button_rect.collidepoint(pos):
                self.state = GameState.MENU
            else:
                for i, rect in enumerate(self.ui.level_button_rects):
                    if rect.collidepoint(pos) and i <= self.unlocked_levels:
                        self.current_level = i
                        self.initialize_level()
                        self.state = GameState.PLAYING
        
        elif self.state == GameState.SETTINGS:
            if self.ui.back_button_rect.collidepoint(pos):
                self.state = GameState.PLAYING if self.level else GameState.MENU
            elif self.ui.volume_rect.collidepoint(pos):
                self.settings["volume"] = (self.settings["volume"] + 0.2) % 1.2
                if self.settings["volume"] > 1.0:
                    self.settings["volume"] = 0.0
                pygame.mixer.music.set_volume(self.settings["volume"])
            elif self.ui.vibration_rect.collidepoint(pos):
                self.settings["vibration"] = not self.settings["vibration"]
            elif self.ui.music_rect.collidepoint(pos):
                self.settings["music"] = not self.settings["music"]
                if self.settings["music"]:
                    pygame.mixer.music.play(-1)
                else:
                    pygame.mixer.music.stop()
            elif self.ui.ai_mode_rect.collidepoint(pos):
                self.toggle_ai_mode()
            elif self.ui.free_movement_rect.collidepoint(pos):
                self.toggle_free_movement()
            elif self.ui.auto_play_rect.collidepoint(pos):
                self.toggle_auto_play()
            elif self.ui.compare_algorithms_button_rect.collidepoint(pos):
                # Chọn hai thuật toán để so sánh
                if len(self.ui.algorithm_values) >= 2:
                    algorithm1 = self.ui.algorithm_values[0]
                    algorithm2 = self.ui.algorithm_values[1]
                    self.compare_algorithms(algorithm1, algorithm2)
            else:
                # Kiểm tra các nút thuật toán
                for i, rect in enumerate(self.ui.algorithm_button_rects):
                    if rect.collidepoint(pos) and i < len(self.ui.algorithm_values):
                        self.settings["ai_algorithm"] = self.ui.algorithm_values[i]
        
        elif self.state == GameState.PLAYING:
            if self.ui.settings_rect.collidepoint(pos):
                self.state = GameState.SETTINGS
            elif self.ui.home_button_rect.collidepoint(pos):
                self.state = GameState.MENU
            elif self.ui.hint_button_rect.collidepoint(pos):
                self.get_hint()
            elif self.comparison_results and hasattr(self, 'close_comparison_button_rect') and self.close_comparison_button_rect.collidepoint(pos):
                self.comparison_results = None
            else:
                # Kiểm tra các nút thuật toán
                for i, rect in enumerate(self.ui.algorithm_button_rects):
                    if rect.collidepoint(pos) and i < len(self.ui.algorithm_values):
                        self.settings["ai_algorithm"] = self.ui.algorithm_values[i]
                        return
                
                # Kiểm tra nút so sánh thuật toán
                if self.ui.compare_algorithms_button_rect.collidepoint(pos):
                    if len(self.ui.algorithm_values) >= 2:
                        algorithm1 = self.ui.algorithm_values[0]
                        algorithm2 = self.ui.algorithm_values[1]
                        self.compare_algorithms(algorithm1, algorithm2)
                    return
                
                # Xử lý click vào lưới kẹo
                grid_pos = self.get_grid_position(pos)
                if grid_pos:
                    row, col = grid_pos
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        if self.settings["free_movement"]:
                            # Chế độ kéo thả tự do
                            if not self.selected_candy:
                                self.selected_candy = (row, col)
                                self.dragging = True
                                self.drag_start_pos = pos
                            else:
                                sel_row, sel_col = self.selected_candy
                                if abs(row - sel_row) + abs(col - sel_col) == 1:
                                    # Hoán đổi kẹo nếu chúng kề nhau
                                    if self.try_swap_candies(sel_row, sel_col, row, col):
                                        self.level.moves_left -= 1
                                self.selected_candy = None
                                self.dragging = False
                        else:
                            # Chế độ chọn và click
                            if not self.selected_candy:
                                self.selected_candy = (row, col)
                            else:
                                sel_row, sel_col = self.selected_candy
                                if (row == sel_row and col == sel_col):
                                    # Click lại vào cùng một kẹo, bỏ chọn
                                    self.selected_candy = None
                                elif abs(row - sel_row) + abs(col - sel_col) == 1:
                                    # Hoán đổi kẹo nếu chúng kề nhau
                                    if self.try_swap_candies(sel_row, sel_col, row, col):
                                        self.level.moves_left -= 1
                                    self.selected_candy = None
                                else:
                                    # Chọn kẹo mới
                                    self.selected_candy = (row, col)
        
        elif self.state in (GameState.GAME_OVER, GameState.LEVEL_COMPLETE):
            if self.ui.play_button_rect.collidepoint(pos):
                if self.state == GameState.GAME_OVER:
                    # Chơi lại cấp độ hiện tại
                    self.reset_level()
                    self.state = GameState.PLAYING
                else:  # LEVEL_COMPLETE
                    # Mở khóa cấp độ tiếp theo nếu có
                    if self.current_level == self.unlocked_levels:
                        self.unlocked_levels = min(self.unlocked_levels + 1, len(self.levels) - 1)
                    
                    # Chuyển đến cấp độ tiếp theo nếu có
                    if self.current_level < len(self.levels) - 1:
                        self.current_level += 1
                        self.initialize_level()
                        self.state = GameState.PLAYING
                    else:
                        # Đã hoàn thành tất cả các cấp độ
                        self.state = GameState.MENU

    def check_and_fill_board(self):
        """Kiểm tra và điền các ô trống trên bảng"""
        # Kiểm tra xem có kẹo nào đang di chuyển không
        any_moving = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] is not None and self.board[row][col].moving:
                    any_moving = True
                    break
        
        if not any_moving:
            # Di chuyển kẹo xuống để lấp đầy khoảng trống
            self.level.shift_candies_down()
            
            # Điền các ô trống với kẹo mới
            self.level.fill_empty_spaces()
