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
            
            # Tải các file âm thanh
            self.pop_sound = pygame.mixer.Sound(os.path.join(assets_dir, "in-game-level-uptype-2-230567.mp3"))
            self.swap_sound = pygame.mixer.Sound(os.path.join(assets_dir, "in-game-level-uptype-2-230567.mp3"))
            self.match_sound = pygame.mixer.Sound(os.path.join(assets_dir, "in-game-level-uptype-2-230567.mp3"))
            self.game_over_sound = pygame.mixer.Sound(os.path.join(assets_dir, "game-over-39-199830.mp3"))
            self.level_complete_sound = pygame.mixer.Sound(os.path.join(assets_dir, "in-game-level-uptype-2-230567.mp3"))
            
            # Tải nhạc nền
            pygame.mixer.music.load(os.path.join(assets_dir, "game-music-loop-7-145285.mp3"))
            pygame.mixer.music.set_volume(0.5)
            
        except Exception as e:
            print(f"Không thể khởi tạo hệ thống âm thanh: {str(e)}")
            class DummySound:
                def play(self):
                    pass
            self.pop_sound = DummySound()
            self.swap_sound = DummySound()
            self.match_sound = DummySound()
            self.game_over_sound = DummySound()
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
        
        # Định nghĩa các cấp độ
        self.levels = [
            {"target_score": 800, "moves_left": 20, "level_type": LevelType.SCORE},
            {"target_score": 1000, "moves_left": 20, "level_type": LevelType.JELLY},
            {"target_score": 1200, "moves_left": 15, "level_type": LevelType.SCORE},
        ]
        self.current_level = 0
        self.unlocked_levels = 0
        self.state = GameState.MENU
        
        # Khởi tạo cấp độ
        self.level = None

        # Biến cho việc chọn và di chuyển kẹo
        self.selected_candy = None
        
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
        self.swap_animation_duration = 0.2
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
            "music": True,
            "ai_mode": False,
            "ai_algorithm": "hybrid",
            "auto_play": False,
            "sound": True,
            "vibration": True,
            "free_movement": False,
            "sound_effects": True
        }

        # Khởi tạo cấp độ sau khi đã có settings
        self.initialize_level()
        
        # Biến cho chế độ tự động chơi
        self.auto_play_timer = 0
        self.auto_play_interval = 0.8
        
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
        self.hint_start_time = 0
        self.hint_duration = 3.0
        self.show_hint = False
        
        # Biến cho nước đi không hợp lệ
        self.invalid_move = False
        self.invalid_move_time = 0
        self.invalid_move_duration = 0.3
        self.invalid_move_positions = None

        # Thêm biến để theo dõi trạng thái hiển thị các nút thuật toán AI
        self.showing_ai_buttons = False
        
        # Thêm biến để đo thời gian thực thi thuật toán
        # Khởi tạo với tất cả thuật toán có thể có, bao gồm and_or, backtracking, và q_learning
        self.algorithm_execution_times = {
            "hybrid": 0.0,
            "minimax": 0.0,
            "simulated_annealing": 0.0,
            "bfs": 0.0,
            "a_star": 0.0,
            "and_or": 0.0,  # Thêm and_or
            "backtracking": 0.0,  # Thêm backtracking
            "q_learning": 0.0  # Thêm q_learning
        }
        self.algorithm_path_costs = {}
        self.level_start_time = 0.0  # Biến để ghi lại thời gian bắt đầu level

        # Thêm biến để theo dõi trạng thái hiển thị chế độ thuật toán
        self.showing_algorithm_mode = False

        # Thêm biến để theo dõi trạng thái hoàn thành level 1
        self.level1_completed = False

        # Thêm biến để theo dõi trạng thái tạm dừng trò chơi
        self.game_paused = False
        
        # Thêm lịch sử nước đi, thời gian và thuật toán
        self.move_history = {level: [] for level in range(len(self.levels))}
        self.time_history = {level: [] for level in range(len(self.levels))}
        self.cost_history = {level: [] for level in range(len(self.levels))}
        self.algorithm_history = {level: [] for level in range(len(self.levels))}  # Lưu thuật toán cho mỗi nước đi
    
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
        self.level_start_time = time.time()  # Ghi lại thời gian bắt đầu level
        level_info = self.levels[self.current_level]
        level_type = level_info["level_type"]
        self.level = create_level(level_type, self.current_level + 1)
        self.level.moves_left = level_info["moves_left"]
        self.level.target_score = level_info["target_score"]
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
        
        # Phát nhạc nền nếu chế độ âm nhạc được bật
        if self.settings["music"]:
            pygame.mixer.music.play(-1)  # -1 để lặp vô hạn
        
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

        if self.current_level > 0:
            self.level1_completed = True
    
    def reset_level(self):
        self.initialize_level()
        self.selected_candy = None
    
    def toggle_ai_mode(self):
        self.settings["ai_mode"] = not self.settings["ai_mode"]
        if self.settings["ai_mode"]:
            self.settings["auto_play"] = False
    
    def toggle_auto_play(self):
        self.settings["auto_play"] = not self.settings["auto_play"]
        if self.settings["auto_play"]:
            self.settings["ai_mode"] = False
            self.auto_play_timer = time.time()
    
    def toggle_pause_game(self):
        """Tạm dừng hoặc tiếp tục trò chơi"""
        self.game_paused = not self.game_paused
        if self.game_paused:
            self.ui.show_message("Tro choi da tam dung", 1000)
        else:
            self.ui.show_message("Tro choi tiep tuc", 1000)
    
    def get_hint(self):
        self.hint_move = self.ai.get_best_move(
            algorithm=self.settings["ai_algorithm"],
            max_depth=2,
            iterations=5 if self.settings["ai_algorithm"] != "simulated_annealing" else 500
        )
        self.show_hint = True
        self.hint_start_time = time.time()
        self.hint_duration = 3.0  # Hiệu ứng gợi ý hiển thị trong 3 giây

    def compare_algorithms(self, algorithm1, algorithm2):
        """So sánh hiệu suất của tất cả thuật toán đã chọn"""
        if len(self.ui.selected_algorithms) < 2:
            print("Can it nhat 2 thuat toan de so sanh")
            self.ui.show_message("Can it nhat 2 thuat toan de so sanh", 2000)
            return None

        self.comparing_algorithms = True
        
        # Lưu trữ kết quả cho tất cả thuật toán đã chọn
        results = {
            "algorithms": [],
            "total_times": [],
            "total_costs": [],
            "total_scores": [],
            "efficiencies": []
        }
        
        completed_levels = self.current_level + 1  # Số level đã hoàn thành
        
        print(f"Bat dau so sanh cac thuat toan {self.ui.selected_algorithms} dựa trên {completed_levels} level...")
        
        # Tính toán cho từng thuật toán đã chọn
        for algo in self.ui.selected_algorithms:
            total_time = self.algorithm_execution_times.get(algo, 0.0)  # Sử dụng tổng thời gian từ algorithm_execution_times
            total_cost = 0
            total_score = 0
            move_count = 0
            
            # Tính tổng chi phí và điểm từ lịch sử
            for level in range(completed_levels):
                for i, (move, algo_used) in enumerate(zip(self.move_history[level], self.algorithm_history[level])):
                    if algo_used == algo and i < len(self.cost_history[level]):
                        path_cost = self.cost_history[level][i]
                        total_cost += path_cost
                        move_count += 1
                
                # Lấy điểm từ level đã hoàn thành
                if self.level.score and move_count > 0:
                    total_score += self.level.score
            
            if move_count == 0:
                print(f"Khong co du lieu thuc te cho thuat toan {algo}. Vui long su dung thuat toan này de choi truoc.")
                self.ui.show_message(f"Khong co du lieu cho {algo}. Vui long choi voi thuat toan nay truoc.", 2000)
                self.comparing_algorithms = False
                return None
            
            # Tính hiệu suất (điểm chia thời gian)
            efficiency = total_score / total_time if total_time > 0 else 0
            
            # Lưu kết quả
            results["algorithms"].append(algo)
            results["total_times"].append(total_time)
            results["total_costs"].append(total_cost)
            results["total_scores"].append(total_score)
            results["efficiencies"].append(efficiency)
        
        # Xác định thuật toán tốt nhất
        best_score = max(results["total_scores"])
        best_idx = results["total_scores"].index(best_score)
        better_algorithm = results["algorithms"][best_idx]
        score_diff = best_score - min(results["total_scores"])
        
        # Thêm thông tin về thuật toán tốt nhất
        results["better_algorithm"] = better_algorithm
        results["score_diff"] = score_diff
        
        self.comparison_results = results
        
        print(f"Ket qua so sanh: {self.comparison_results}")
        self.comparing_algorithms = False
        
        return self.comparison_results

    def draw_comparison_results(self):
        """Hiển thị kết quả so sánh thuật toán với biểu đồ cột"""
        if not self.comparison_results or not isinstance(self.comparison_results, dict):
            return
        
        required_keys = ["algorithms", "total_times", "total_costs", "total_scores", 
                        "efficiencies", "better_algorithm", "score_diff"]
        if not all(key in self.comparison_results for key in required_keys):
            print("Du lieu comparison_results thieu mot hoac nhieu khoa can thiet:", self.comparison_results)
            return
        
        from chart import Chart
        chart = Chart(self.screen)
        
        # Chuẩn bị dữ liệu cho biểu đồ
        comparison_data = {
            "algorithms": self.comparison_results["algorithms"],
            "total_time_data": [],
            "total_cost_data": []
        }
        
        # Tạo dữ liệu cho biểu đồ thời gian
        colors = [(41, 128, 185), (230, 126, 34), (39, 174, 96)]  # Màu sắc cho các thuật toán
        for i, algo in enumerate(self.comparison_results["algorithms"]):
            time_data = (algo, self.comparison_results["total_times"][i], colors[i % len(colors)])
            cost_data = (algo, self.comparison_results["total_costs"][i], colors[i % len(colors)])
            comparison_data["total_time_data"].append(time_data)
            comparison_data["total_cost_data"].append(time_data)
        
        # Vẽ biểu đồ
        chart.draw_comparison_chart(comparison_data)
        
        self.close_comparison_button_rect = chart.close_button_rect
    
    def make_ai_move(self):
        if not self.swapping and not self.waiting_for_animations:
            start_time = time.time()
            iterations = 5 if self.settings["ai_algorithm"] != "simulated_annealing" else 500
            best_move = self.ai.get_best_move(
                algorithm=self.settings["ai_algorithm"],
                max_depth=2,
                iterations=iterations
            )
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Thuat toan: {self.settings['ai_algorithm']}, Nuoc di: {best_move}, Thoi gian: {execution_time:.3f} Giay, Iterations: {iterations}")
            if best_move:
                row1, col1, row2, col2 = best_move
                success = self.try_swap_candies(row1, col1, row2, col2)
                if success:
                    self.level.moves_left -= 1
                    path_cost = abs(row2 - row1) + abs(col2 - col1)
                    self.move_history[self.current_level].append((row1, col1, row2, col2))
                    self.time_history[self.current_level].append(execution_time)
                    self.cost_history[self.current_level].append(path_cost)
                    self.algorithm_history[self.current_level].append(self.settings["ai_algorithm"])
    
    def auto_play_move(self):
        current_time = time.time()
        if current_time - self.auto_play_timer >= self.auto_play_interval:
            self.make_ai_move()
            self.auto_play_timer = current_time
    
    def draw_hint(self):
        if self.show_hint and self.hint_move:
            current_time = time.time()
            # Chỉ hiển thị hiệu ứng gợi ý trong khoảng thời gian nhất định
            if current_time - self.hint_start_time < self.hint_duration:
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
            if self.game_paused:
                return
            
            current_time = time.time()
            
            if self.swapping:
                elapsed_time = current_time - self.swap_start_time
                if elapsed_time >= self.swap_animation_duration:
                    self.swapping = False
                    if self.swap_back_animation:
                        self.swap_back_animation = False
                        if self.board[self.swap_row1][self.swap_col1]:
                            self.board[self.swap_row1][self.swap_col1].x = GRID_OFFSET_X + self.swap_col1 * CELL_SIZE
                            self.board[self.swap_row1][self.swap_row1][self.swap_col1].y = GRID_OFFSET_Y + self.swap_row1 * CELL_SIZE
                            self.board[self.swap_row1][self.swap_col1].target_x = self.board[self.swap_row1][self.swap_col1].x
                            self.board[self.swap_row1][self.swap_col1].target_y = self.board[self.swap_row1][self.swap_col1].y
                        if self.board[self.swap_row2][self.swap_col2]:
                            self.board[self.swap_row2][self.swap_col2].x = GRID_OFFSET_X + self.swap_col2 * CELL_SIZE
                            self.board[self.swap_row2][self.swap_col2].y = GRID_OFFSET_Y + self.swap_row2 * CELL_SIZE
                            self.board[self.swap_row2][self.swap_col2].target_x = self.board[self.swap_row2][self.swap_col2].x
                            self.board[self.swap_row2][self.swap_col2].target_y = self.board[self.swap_row2][self.swap_col2].y
            if self.invalid_move:
                elapsed_time = current_time - self.invalid_move_time
                if elapsed_time >= self.invalid_move_duration:
                    self.invalid_move = False
                    self.invalid_move_positions = None
            
            any_moving = False
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.board[row][col]:
                        self.board[row][col].update()
                        if self.board[row][col].moving:
                            any_moving = True
            
            self.waiting_for_animations = any_moving or self.swapping
            
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
            
            if hasattr(self.level, 'wrapped_explosion_pending') and self.level.wrapped_explosion_pending:
                for row, col in self.level.wrapped_explosion_pending[:]:
                    if (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and 
                        self.board[row][col] is not None and 
                        self.board[row][col].special_type == SpecialType.WRAPPED):
                        self.level.explode_wrapped_candy(row, col, is_second_explosion=True)
                        self.board[row][col].remove = True
                self.level.wrapped_explosion_pending = []
            
            if self.level.is_level_complete():
                # Tính thời gian của level và cộng vào tổng thời gian của thuật toán
                level_end_time = time.time()
                level_time = level_end_time - self.level_start_time
                current_algorithm = self.settings["ai_algorithm"]
                self.algorithm_execution_times[current_algorithm] += level_time
                print(f"Level {self.current_level + 1} complete! Score: {self.level.score}, "
                      f"Thoi gian level: {level_time:.2f}s, Tong thoi gian ({current_algorithm}): "
                      f"{self.algorithm_execution_times[current_algorithm]:.2f}s")
                if self.level_type == LevelType.JELLY:
                    print(f"Jellies left: {self.level.jellies_left}")
                elif self.level_type == LevelType.CHOCOLATE:
                    print(f"Chocolates left: {self.level.chocolates_left}")
                self.state = GameState.LEVEL_COMPLETE
                self.level_complete_sound.play()
            elif self.level.moves_left <= 0 and not self.level.is_level_complete():
                # Tính thời gian của level và cộng vào tổng thời gian của thuật toán
                level_end_time = time.time()
                level_time = level_end_time - self.level_start_time
                current_algorithm = self.settings["ai_algorithm"]
                self.algorithm_execution_times[current_algorithm] += level_time
                print(f"Game over! Level {self.current_level + 1} failed. Score: {self.level.score}, "
                      f"Thoi gian level: {level_time:.2f}s, Tong thoi gian ({current_algorithm}): "
                      f"{self.algorithm_execution_times[current_algorithm]:.2f}s")
                if self.level_type == LevelType.JELLY:
                    print(f"Jellies left: {self.level.jellies_left}")
                elif self.level_type == LevelType.CHOCOLATE:
                    print(f"Chocolates left: {self.level.chocolates_left}")
                self.state = GameState.GAME_OVER
                pygame.mixer.music.stop()  # Dừng nhạc nền
                self.game_over_sound.play()  # Phát âm thanh game over

            if self.level.is_level_complete() and self.current_level == 0:
                self.level1_completed = True
            
            if self.settings["ai_mode"] and not self.waiting_for_animations and not self.game_paused:
                self.make_ai_move()
            if self.settings["auto_play"] and not self.waiting_for_animations and not self.game_paused:
                self.auto_play_move()
    
    def check_and_fill_board(self):
        """Kiểm tra và điền bảng"""
        any_moving = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] is not None and self.board[row][col].moving:
                    any_moving = True
                    break
        
        if not any_moving:
            empty_count = sum(1 for row in range(GRID_SIZE) for col in range(GRID_SIZE) if self.board[row][col] is None)
            
            if empty_count > 0:
                self.level.shift_candies_down()
                self.level.fill_empty_spaces()
                return True
        
        return False

    def change_algorithm(self, algorithm):
        """Thay đổi thuật toán và reset về level 1"""
        if self.settings["ai_algorithm"] != algorithm:
            self.settings["ai_algorithm"] = algorithm
            self.ui.show_message(f"Da chuyen sang che do thuat toan {algorithm}. Bat dau lai tu level 1.", 1500)
            self.current_level = 0
            self.initialize_level()
            self.state = GameState.PLAYING
            self.settings["ai_mode"] = True
    
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

            if self.selected_candy and not self.dragging and not self.swapping and not self.waiting_for_animations:
                row, col = self.selected_candy
                rect = pygame.Rect(
                    GRID_OFFSET_X + col * CELL_SIZE, 
                    GRID_OFFSET_Y + row * CELL_SIZE, 
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)
            
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
            
            # Vẽ các nút ở vị trí gần nút gợi ý
            if not self.showing_algorithm_mode:
                button_width = 200
                button_height = 40
                button_spacing = 10
                # Đặt nút "Chế độ thuật toán" ngay dưới nút gợi ý
                self.ui.algorithm_mode_button_rect = pygame.Rect(
                    SCREEN_WIDTH - button_width - 20,  # Cách mép phải 20 pixel
                    self.ui.hint_button_rect.bottom + button_spacing,  # Ngay dưới nút gợi ý
                    button_width, button_height
                )
                # Đặt nút "So sánh thuật toán" ngay dưới nút "Chế độ thuật toán"
                self.ui.compare_algorithms_button_rect = pygame.Rect(
                    SCREEN_WIDTH - button_width - 20,
                    self.ui.algorithm_mode_button_rect.bottom + button_spacing,
                    button_width, button_height
                )
                self.screen.blit(self.ui.algorithm_mode_button, self.ui.algorithm_mode_button_rect)
                self.ui.draw_text("Che do thuat toan", self.ui.algorithm_mode_button_rect.center, 20, WHITE)
                self.screen.blit(self.ui.compare_algorithms_button, self.ui.compare_algorithms_button_rect)
                self.ui.draw_text("So sanh thuat toan", self.ui.compare_algorithms_button_rect.center, 20, WHITE)
        
            # Vẽ các nút thuật toán nếu đang ở chế độ chọn thuật toán
            if self.showing_algorithm_mode:
                print(f"Drawing algorithm buttons. showing_algorithm_mode = {self.showing_algorithm_mode}, state = {self.state}")
                self.ui.draw_algorithm_buttons(self.settings)
        
        elif self.state == GameState.SETTINGS:
            self.ui.draw_settings(self.settings)
        
        elif self.state in (GameState.GAME_OVER, GameState.LEVEL_COMPLETE):
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            font = pygame.font.SysFont(None, 72)
            text = font.render("Game Over!" if self.state == GameState.GAME_OVER else "Level Complete!", True, (255, 0, 0) if self.state == GameState.GAME_OVER else (0, 255, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(text, text_rect)
            score_font = pygame.font.SysFont(None, 48)
            score_text = score_font.render(f"Điểm: {self.level.score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(score_text, score_rect)
        
        if self.state == GameState.GAME_OVER:
            # Vẽ nút "Thử lại" trong màn hình Game Over
            retry_button = pygame.Surface((200, 60), pygame.SRCALPHA)
            retry_button.fill((200, 100, 100, 220))  # Màu đỏ nhạt
            retry_button_rect = retry_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            pygame.draw.rect(retry_button, (255, 255, 255, 100), (0, 0, 200, 60), 2, border_radius=10)
            self.screen.blit(retry_button, retry_button_rect)
            
            button_font = pygame.font.SysFont(None, 36)
            button_text = button_font.render("Thử lại", True, (255, 255, 255))
            button_text_rect = button_text.get_rect(center=retry_button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            # Lưu rect của nút để xử lý sự kiện click
            self.retry_button_rect = retry_button_rect
        elif self.state == GameState.LEVEL_COMPLETE:
            # Vẽ nút "Cấp độ tiếp theo" cho màn hình Level Complete
            # Đặt nút dưới hai nút thuật toán
            pygame.draw.rect(self.screen, (100, 150, 200), self.ui.next_level_algorithm_mode_button_rect, border_radius=5)
            self.ui.draw_text("Chế độ Thuật Toán", self.ui.next_level_algorithm_mode_button_rect.center, 20, WHITE)
            
            pygame.draw.rect(self.screen, (100, 150, 200), self.ui.next_level_compare_algorithms_button_rect, border_radius=5)
            self.ui.draw_text("So sánh thuật toán", self.ui.next_level_compare_algorithms_button_rect.center, 20, WHITE)
            
            # Tạo nút "Cấp độ tiếp theo" dưới hai nút thuật toán
            next_level_button = pygame.Surface((200, 60), pygame.SRCALPHA)
            next_level_button.fill((0, 200, 0, 220))  # Màu xanh lá
            next_level_button_rect = next_level_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 220))
            pygame.draw.rect(next_level_button, (255, 255, 255, 100), (0, 0, 200, 60), 2, border_radius=10)
            self.screen.blit(next_level_button, next_level_button_rect)
            
            button_font = pygame.font.SysFont(None, 36)
            button_text = button_font.render("Cap do tiep theo", True, (255, 255, 255))
            button_text_rect = button_text.get_rect(center=next_level_button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            # Lưu rect của nút để xử lý sự kiện click
            self.next_level_button_rect = next_level_button_rect
        
        if self.state == GameState.LEVEL_COMPLETE:
            pygame.draw.rect(self.screen, (100, 150, 200), self.ui.next_level_algorithm_mode_button_rect, border_radius=5)
            self.ui.draw_text("Che do thuat toan", self.ui.next_level_algorithm_mode_button_rect.center, 20, WHITE)
            
            pygame.draw.rect(self.screen, (100, 150, 200), self.ui.next_level_compare_algorithms_button_rect, border_radius=5)
            self.ui.draw_text("So sanh thuat toan", self.ui.next_level_compare_algorithms_button_rect.center, 20, WHITE)
            
        # Chỉ vẽ biểu đồ so sánh nếu comparison_results tồn tại
        if self.comparison_results:
            self.draw_comparison_results()

        # Vẽ các nút thuật toán nếu đang ở chế độ chọn thuật toán (bất kể trạng thái game)
        if self.showing_algorithm_mode:
            print(f"Dang ve cac nut thuat toan o cuoi ham draw. State: {self.state}")
            self.ui.draw_algorithm_buttons(self.settings)
    
    def get_grid_position(self, mouse_pos):
        """Lấy vị trí lưới từ vị trí chuột"""
        if (GRID_OFFSET_X <= mouse_pos[0] <= GRID_OFFSET_X + GRID_SIZE * CELL_SIZE and
            GRID_OFFSET_Y <= mouse_pos[1] <= GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE):
            col = (mouse_pos[0] - GRID_OFFSET_X) // CELL_SIZE
            row = (mouse_pos[1] - GRID_OFFSET_Y) // CELL_SIZE
            return row, col
        return None
    
    def try_swap_candies(self, row1, col1, row2, col2):
        """Thử hoán đổi kẹo"""
        if not (0 <= row1 < GRID_SIZE and 0 <= col1 < GRID_SIZE and 
                0 <= row2 < GRID_SIZE and 0 <= col2 < GRID_SIZE):
            return False
        
        if abs(row1 - row2) + abs(col1 - col2) != 1:
            return False
        
        if (self.board[row1][col1] is None or self.board[row2][col2] is None or
            self.board[row1][col1].blocker_type in [BlockerType.STONE, BlockerType.LOCK, BlockerType.LICORICE] or
            self.board[row2][col2].blocker_type in [BlockerType.STONE, BlockerType.LOCK, BlockerType.LICORICE]):
            self.invalid_move = True
            self.invalid_move_time = time.time()
            self.invalid_move_positions = (row1, col1, row2, col2)
            return False
        
        if self.level.check_special_combination(row1, col1, row2, col2):
            if self.settings["sound_effects"]:
                self.swap_sound.play()
            self.swapping = True
            self.swap_start_time = time.time()
            self.swap_row1, self.swap_col1 = row1, col1
            self.swap_row2, self.swap_col2 = row2, col2
            return True
        
        self.level.swap_candies(row1, col1, row2, col2)
        
        self.swapping = True
        self.swap_start_time = time.time()
        self.swap_row1, self.swap_col1 = row1, col1
        self.swap_row2, self.swap_col2 = row2, col2
        if self.settings["sound_effects"]:
            self.swap_sound.play()
        
        if self.level.find_matches():
            if self.settings["sound_effects"]:
                self.match_sound.play()
            return True
        else:
            self.swap_back_animation = True
            self.level.swap_candies(row1, col1, row2, col2)
            self.invalid_move = True
            self.invalid_move_time = time.time()
            self.invalid_move_positions = (row1, col1, row2, col2)
            return False

    def handle_mouse_down(self, pos):
        """Xử lý sự kiện nhấn chuột"""
        # Kiểm tra trước tiên xem có nhấp vào nút đóng của biểu đồ so sánh không
        if self.comparison_results and hasattr(self, 'close_comparison_button_rect') and self.close_comparison_button_rect:
            if self.close_comparison_button_rect.collidepoint(pos):
                print("Nhấn nút đóng biểu đồ so sánh")
                self.comparison_results = None
                self.close_comparison_button_rect = None  # Đặt lại để tránh xung đột
                # Buộc vẽ lại giao diện ngay lập tức để bỏ biểu đồ
                self.draw()
                pygame.display.flip()
                return

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
            elif hasattr(self.ui, 'sound_effects_rect') and self.ui.sound_effects_rect.collidepoint(pos):
                self.settings["sound_effects"] = not self.settings["sound_effects"]
            elif self.ui.free_movement_rect.collidepoint(pos):
                self.toggle_free_movement()
        
        elif self.state == GameState.PLAYING:
            print(f"showing_algorithm_mode: {self.showing_algorithm_mode}")
            if self.showing_algorithm_mode:
                if hasattr(self.ui, 'close_algorithm_button_rect') and self.ui.close_algorithm_button_rect.collidepoint(pos):
                    self.showing_algorithm_mode = False
                    return
                
                for i, rect in enumerate(self.ui.algorithm_button_rects):
                    if rect.collidepoint(pos) and i < len(self.ui.algorithm_values):
                        algorithm_value = self.ui.algorithm_values[i]
                        if self.settings["ai_algorithm"] == algorithm_value:
                            if algorithm_value not in self.ui.selected_algorithms:
                                self.ui.selected_algorithms.append(algorithm_value)
                                self.ui.show_message(f"Da them {algorithm_value} vao danh sach so sanh", 1000)
                            else:
                                self.ui.selected_algorithms.remove(algorithm_value)
                                self.ui.show_message(f"Da xoa {algorithm_value} khoi sanh sach so sanh", 1000)
                        else:
                            self.change_algorithm(algorithm_value)
                            if algorithm_value not in self.ui.selected_algorithms:
                                self.ui.selected_algorithms.append(algorithm_value)
                        return
                
                if len(self.ui.selected_algorithms) >= 2 and hasattr(self.ui, 'compare_algorithms_button_rect') and self.ui.compare_algorithms_button_rect.collidepoint(pos):
                    if not self.level1_completed:
                        self.ui.show_message("Hay hoan thanh level 1 truoc khi so sanh thuat toan!", 2000)
                        return
                    self.ui.show_message(f"Dang so sanh các thuat toan {', '.join(self.ui.selected_algorithms)}...", 1000)
                    self.compare_algorithms(None, None)  # Không cần truyền algorithm1, algorithm2 vì dùng tất cả selected_algorithms
                    self.showing_algorithm_mode = False
                    return
                return
            
            elif self.ui.pause_button_rect.collidepoint(pos) and not self.game_paused:
                self.toggle_pause_game()
            elif self.ui.resume_button_rect.collidepoint(pos) and self.game_paused:
                self.toggle_pause_game()
            elif self.ui.menu_level_button_rect.collidepoint(pos):
                self.state = GameState.LEVEL_SELECT

            if self.ui.settings_rect.collidepoint(pos):
                self.state = GameState.SETTINGS
            elif self.ui.home_button_rect.collidepoint(pos):
                self.state = GameState.MENU
            elif self.ui.hint_button_rect.collidepoint(pos):
                self.get_hint()
            elif self.ui.algorithm_mode_button_rect.collidepoint(pos):
                self.showing_algorithm_mode = True
                return
            elif self.ui.compare_algorithms_button_rect.collidepoint(pos):
                if not self.level1_completed:
                    self.ui.show_message("Hay hoan thanh level 1 truoc khi so sanh thuat toan!", 2000)
                    return
                if len(self.ui.selected_algorithms) < 2:
                    self.ui.show_message("Can chon it nhat 2 thuat toan de so sanh. Vao che do thuat toan de chon.", 2000)
                    return
                self.ui.show_message(f"Dang so sanh thuat toan{', '.join(self.ui.selected_algorithms)}...", 1000)
                self.compare_algorithms(None, None)  # Không cần truyền algorithm1, algorithm2 vì dùng tất cả selected_algorithms
                return
            else:
                grid_pos = self.get_grid_position(pos)
                if grid_pos:
                    row, col = grid_pos
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        if self.settings["free_movement"]:
                            if not self.selected_candy:
                                self.selected_candy = (row, col)
                                self.dragging = True
                                self.drag_start_pos = pos
                            else:
                                sel_row, sel_col = self.selected_candy
                                if abs(row - sel_row) + abs(col - sel_col) == 1:
                                    if self.try_swap_candies(sel_row, sel_col, row, col):
                                        self.level.moves_left -= 1
                                self.selected_candy = None
                                self.dragging = False
                        else:
                            if not self.selected_candy:
                                self.selected_candy = (row, col)
                            else:
                                sel_row, sel_col = self.selected_candy
                                if (row == sel_row and col == sel_col):
                                    self.selected_candy = None
                                elif abs(row - sel_row) + abs(col - sel_col) == 1:
                                    if self.try_swap_candies(sel_row, sel_col, row, col):
                                        self.level.moves_left -= 1
                                    self.selected_candy = None
                                else:
                                    self.selected_candy = (row, col)
        
        elif self.state in (GameState.GAME_OVER, GameState.LEVEL_COMPLETE):
            # Kiểm tra nút đóng của biểu đồ so sánh trong trạng thái GAME_OVER hoặc LEVEL_COMPLETE
            if self.comparison_results and hasattr(self, 'close_comparison_button_rect') and self.close_comparison_button_rect:
                if self.close_comparison_button_rect.collidepoint(pos):
                    print("Nhấn nút đóng biểu đồ so sánh trong trạng thái GAME_OVER/LEVEL_COMPLETE")
                    self.comparison_results = None
                    self.close_comparison_button_rect = None
                    self.draw()
                    pygame.display.flip()
                    return

            if self.state == GameState.GAME_OVER and hasattr(self, 'retry_button_rect') and self.retry_button_rect.collidepoint(pos):
                self.reset_level()
                self.state = GameState.PLAYING
            elif self.state == GameState.LEVEL_COMPLETE and hasattr(self, 'next_level_button_rect') and self.next_level_button_rect.collidepoint(pos):
                if self.current_level == self.unlocked_levels:
                    self.unlocked_levels = min(self.unlocked_levels + 1, len(self.levels) - 1)
                if self.current_level < len(self.levels) - 1:
                    self.current_level += 1
                    self.initialize_level()
                    self.state = GameState.PLAYING
                else:
                    self.state = GameState.MENU
            elif self.ui.next_level_algorithm_mode_button_rect.collidepoint(pos):
                self.showing_algorithm_mode = True
                print(f"Da nhap vao nut che do thuat toan, hien thi cac nut thuat toan. showing_algorithm_mode = {self.showing_algorithm_mode}")
            elif self.ui.next_level_compare_algorithms_button_rect.collidepoint(pos):
                if not self.level1_completed:
                    self.ui.show_message("Hay hoan thanh level 1 truoc khi so sanh thuat toan", 2000)
                    return
                if len(self.ui.selected_algorithms) < 2:
                    self.ui.show_message("Can chon it nhat 2 thuat toan de so sanh. Vao che do thuat toan de chon.", 2000)
                    return
                self.ui.show_message(f"Dang so sanh cac thuat toan {', '.join(self.ui.selected_algorithms)}...", 1000)
                result = self.compare_algorithms(None, None)
                if result:
                    self.comparison_results = result
                    self.draw_comparison_results()
                    pygame.display.flip()
            elif self.showing_algorithm_mode:
                if self.ui.close_algorithm_button_rect and self.ui.close_algorithm_button_rect.collidepoint(pos):
                    self.showing_algorithm_mode = False
                    print("Da dong lop phu che do thuat toan.")
                    return
                for i, rect in enumerate(self.ui.algorithm_button_rects):
                    if rect.collidepoint(pos) and i < len(self.ui.algorithm_values):
                        algorithm_value = self.ui.algorithm_values[i]
                        if algorithm_value in self.ui.selected_algorithms:
                            self.ui.selected_algorithms.remove(algorithm_value)
                            self.ui.show_message(f"Da xoa {algorithm_value} khoi danh sach so sanh", 1000)
                        else:
                            self.ui.selected_algorithms.append(algorithm_value)
                            self.ui.show_message(f"Da them {algorithm_value} vao danh sach so sanh", 1000)
                        self.change_algorithm(algorithm_value)
                        self.showing_algorithm_mode = False
                        print(f"Đã chọn thuật toán: {algorithm_value}")
                        return
                if self.ui.compare_algorithms_button_rect and self.ui.compare_algorithms_button_rect.collidepoint(pos):
                    if len(self.ui.selected_algorithms) >= 2:
                        self.ui.show_message(f"Dang so sanh cac thuat toan {', '.join(self.ui.selected_algorithms)}...", 1000)
                        self.compare_algorithms(None, None)
                        self.showing_algorithm_mode = False
                        return
