import pygame
from constants import *
import os
import random

class UI:
    def __init__(self, screen):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 72)
        self.game_state = GameState.MENU

        # Sử dụng đường dẫn tương đối
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(script_dir, "assets")
        print(f"UI: Đường dẫn assets: {assets_path}")
        print(f"UI: Thư mục assets tồn tại: {os.path.exists(assets_path)}")
        
        if not os.path.exists(assets_path):
            try:
                os.makedirs(assets_path, exist_ok=True)
                print(f"Đã tạo thư mục assets tại {assets_path}")
            except Exception as e:
                print(f"Không thể tạo thư mục assets: {e}")
        
        if os.path.exists(assets_path):
            print("UI: Các file trong thư mục assets:")
            for file in os.listdir(assets_path):
                print(f"  - {file}")

        # Load background
        try:
            bg_path = os.path.join(assets_path, "level1.png")
            print(f"UI: Đang tải background từ: {bg_path}")
            print(f"UI: File background tồn tại: {os.path.exists(bg_path)}")
            if os.path.exists(bg_path):
                self.background_image = pygame.image.load(bg_path).convert()
                self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            else:
                raise FileNotFoundError(f"Không tìm thấy file background: {bg_path}")
        except Exception as e:
            print(f"UI: Không thể tải background: {e}")
            self.background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background_image.fill((100, 149, 237))
            for i in range(20):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                radius = random.randint(5, 20)
                color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
                pygame.draw.circle(self.background_image, color, (x, y), radius)

        # Load level select background
        try:
            level_select_bg_path = os.path.join(assets_path, "level_select_bg.png")
            if os.path.exists(level_select_bg_path):
                self.level_select_bg = pygame.image.load(level_select_bg_path).convert()
                self.level_select_bg = pygame.transform.scale(self.level_select_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            else:
                self.level_select_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                self.level_select_bg.fill((70, 130, 180))
                for i in range(30):
                    x = random.randint(0, SCREEN_WIDTH)
                    y = random.randint(0, SCREEN_HEIGHT)
                    radius = random.randint(5, 25)
                    color = (random.randint(180, 255), random.randint(180, 255), random.randint(200, 255))
                    pygame.draw.circle(self.level_select_bg, color, (x, y), radius)
        except Exception as e:
            print(f"UI: Không thể tải level select background: {e}")
            self.level_select_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.level_select_bg.fill((70, 130, 180))
            for i in range(30):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                radius = random.randint(5, 25)
                color = (random.randint(180, 255), random.randint(180, 255), random.randint(200, 255))
                pygame.draw.circle(self.level_select_bg, color, (x, y), radius)

        # Load icons and buttons
        try:
            settings_path = os.path.join(assets_path, "button_hover.png")
            print(f"UI: Đang tải settings icon từ: {settings_path}")
            print(f"UI: File settings icon tồn tại: {os.path.exists(settings_path)}")
            if os.path.exists(settings_path):
                self.settings_icon = pygame.image.load(settings_path).convert_alpha()
                self.settings_icon = pygame.transform.scale(self.settings_icon, (60, 60))
            else:
                raise FileNotFoundError(f"Không tìm thấy file settings icon: {settings_path}")
        except Exception as e:
            print(f"UI: Không thể tải settings icon: {e}")
            self.settings_icon = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.settings_icon, (100, 100, 200, 200), (0, 0, 60, 60), border_radius=10)
            pygame.draw.rect(self.settings_icon, (255, 255, 255, 200), (0, 0, 60, 60), 2, border_radius=10)
            pygame.draw.line(self.settings_icon, (255, 255, 255, 200), (15, 20), (45, 20), 4)
            pygame.draw.line(self.settings_icon, (255, 255, 255, 200), (15, 30), (45, 30), 4)
            pygame.draw.line(self.settings_icon, (255, 255, 255, 200), (15, 40), (45, 40), 4)
        
        self.settings_rect = self.settings_icon.get_rect(topright=(SCREEN_WIDTH - 20, 140))

        try:
            button_path = os.path.join(assets_path, "button.png")
            print(f"UI: Đang tải play button từ: {button_path}")
            print(f"UI: File play button tồn tại: {os.path.exists(button_path)}")
            if os.path.exists(button_path):
                self.play_button = pygame.image.load(button_path).convert_alpha()
                self.play_button = pygame.transform.scale(self.play_button, (120, 50))
            else:
                raise FileNotFoundError(f"Không tìm thấy file play button: {button_path}")
        except Exception as e:
            print(f"UI: Không thể tải play button: {e}")
            self.play_button = pygame.Surface((120, 50), pygame.SRCALPHA)
            pygame.draw.rect(self.play_button, (100, 200, 100, 200), (0, 0, 120, 50), border_radius=10)
            pygame.draw.rect(self.play_button, (255, 255, 255, 200), (0, 0, 120, 50), 2, border_radius=10)
        
        self.play_button_rect = self.play_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))

        try:
            level_button_path = os.path.join(assets_path, "button_level.png")
            if os.path.exists(level_button_path):
                self.level_button = pygame.image.load(level_button_path).convert_alpha()
                self.level_button = pygame.transform.scale(self.level_button, (100, 100))
            else:
                self.level_button = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(self.level_button, (200, 100, 100, 200), (50, 50), 45)
                pygame.draw.circle(self.level_button, (255, 255, 255, 200), (50, 50), 45, 2)
        except Exception as e:
            print(f"UI: Không thể tải level button: {e}")
            self.level_button = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(self.level_button, (200, 100, 100, 200), (50, 50), 45)
            pygame.draw.circle(self.level_button, (255, 255, 255, 200), (50, 50), 45, 2)

        try:
            home_button_path = os.path.join(assets_path, "button_home.png")
            if os.path.exists(home_button_path):
                self.home_button = pygame.image.load(home_button_path).convert_alpha()
                self.home_button = pygame.transform.scale(self.home_button, (60, 60))
            else:
                self.home_button = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.rect(self.home_button, (100, 150, 200, 200), (0, 0, 60, 60), border_radius=10)
                pygame.draw.rect(self.home_button, (255, 255, 255, 200), (0, 0, 60, 60), 2, border_radius=10)
                pygame.draw.polygon(self.home_button, (255, 255, 255, 200), [(30, 15), (15, 30), (45, 30)])
                pygame.draw.rect(self.home_button, (255, 255, 255, 200), (20, 30, 20, 15))
        except Exception as e:
            print(f"UI: Không thể tải home button: {e}")
            self.home_button = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.home_button, (100, 150, 200, 200), (0, 0, 60, 60), border_radius=10)
            pygame.draw.rect(self.home_button, (255, 255, 255, 200), (0, 0, 60, 60), 2, border_radius=10)
            pygame.draw.polygon(self.home_button, (255, 255, 255, 200), [(30, 15), (15, 30), (45, 30)])
            pygame.draw.rect(self.home_button, (255, 255, 255, 200), (20, 30, 20, 15))
        
        self.home_button_rect = self.home_button.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))

        self.ai_button = None
        self.ai_button_rect = None
        
        self.hint_button = pygame.Surface((120, 40))
        self.hint_button.fill((200, 100, 100))
        self.hint_button_rect = self.hint_button.get_rect(topright=(SCREEN_WIDTH - 20, 200))

        self.add_moves_button = None
        self.add_moves_button_rect = None

        self.free_movement_button = None
        self.free_movement_button_rect = None

        self.auto_play_button = None
        self.auto_play_button_rect = None

        self.back_button = pygame.Surface((120, 40))
        self.back_button.fill((150, 150, 150))
        self.back_button_rect = pygame.Rect(70, 580, 160, 40)

        # Settings UI rectangles
        self.volume_rect = pygame.Rect(70, 100, 160, 40)
        self.vibration_rect = pygame.Rect(70, 160, 160, 40)
        self.music_rect = pygame.Rect(70, 220, 160, 40)
        self.ai_mode_rect = pygame.Rect(70, 280, 160, 40)
        self.free_movement_rect = pygame.Rect(70, 340, 160, 40)
        self.auto_play_rect = pygame.Rect(70, 400, 160, 40)
        # Algorithm selection rectangles
        # Xóa các rectangle cũ cho các nút thuật toán
        # self.a_star_rect = pygame.Rect(70, 460, 160, 40)
        # self.bfs_rect = pygame.Rect(70, 520, 160, 40)
        # self.backtracking_rect = pygame.Rect(270, 100, 160, 40)
        # self.simulated_annealing_rect = pygame.Rect(270, 160, 160, 40)
        # self.q_learning_rect = pygame.Rect(270, 220, 160, 40)
        # self.and_or_rect = pygame.Rect(270, 280, 160, 40)

        # Thêm nút so sánh thuật toán
        self.compare_algorithms_button = pygame.Surface((200, 40))
        self.compare_algorithms_button.fill((100, 150, 200))
        self.compare_algorithms_button_rect = pygame.Rect(SCREEN_WIDTH - 220, 400, 200, 40)  # Đặt nút ở dưới các nút thuật toán
        
        # Thêm các nút thuật toán
        self.algorithm_buttons = []
        self.algorithm_button_rects = []
        self.algorithm_names = ["A*", "BFS", "Backtracking", "Simulated Annealing", "Q-Learning", "And-Or"]
        self.algorithm_values = ["a_star", "bfs", "backtracking", "simulated_annealing", "q_learning", "and_or"]

        self.level_buttons = []
        self.level_button_rects = []
        self.max_levels_per_row = 3
        self.level_button_size = 100
        self.level_button_margin = 30
        self.level_button_start_y = 150

    def draw_level_info(self, level_number, score, moves_left, level_type, target_score=0,
                        jellies_left=0, ingredients_left=0, chocolates_left=0, blockers_count=0, settings=None):
        self.screen.blit(self.background_image, (0, 0))
        
        self.screen.blit(self.settings_icon, self.settings_rect)
        self.screen.blit(self.home_button, self.home_button_rect)

        self.screen.blit(self.font.render(f"Cap do {level_number}", True, BLACK), (20, 20))
        self.screen.blit(self.font.render(f"Diem: {score}", True, BLACK), (20, 60))
        self.screen.blit(self.font.render(f"Luot: {moves_left}", True, BLACK), (20, 100))

        if level_type == LevelType.SCORE:
            self.screen.blit(self.font.render(f"Muc tieu: {target_score}", True, BLACK), (SCREEN_WIDTH - 200, 20))
            progress = min(1.0, score / target_score) if target_score > 0 else 0
            pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH - 200, 60, 180, 20), border_radius=5)
            pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 200, 60, int(180 * progress), 20), border_radius=5)
        elif level_type == LevelType.JELLY:
            self.screen.blit(self.font.render(f"Keo deo: {jellies_left}", True, BLACK), (SCREEN_WIDTH - 200, 20))
        elif level_type == LevelType.INGREDIENT:
            self.screen.blit(self.font.render(f"Nguyen lieu: {ingredients_left}", True, BLACK), (SCREEN_WIDTH - 200, 20))
        elif level_type == LevelType.CHOCOLATE:
            self.screen.blit(self.font.render(f"So-co-la: {chocolates_left}", True, BLACK), (SCREEN_WIDTH - 200, 20))

        if settings:
            if self.hint_button and self.hint_button_rect:
                self.screen.blit(self.hint_button, self.hint_button_rect)
                self.draw_text("Goi y", self.hint_button_rect.center, 20, WHITE)
                
                # Vẽ các nút thuật toán dưới nút gợi ý
                self.draw_algorithm_buttons(settings)

        if self.game_state in (GameState.LEVEL_COMPLETE, GameState.GAME_OVER):
            self.screen.blit(self.play_button, self.play_button_rect)

    # Fix the algorithm buttons drawing
    def draw_algorithm_buttons(self, settings, y_start=260):
        """Vẽ các nút thuật toán dưới nút gợi ý"""
        self.algorithm_buttons = []
        self.algorithm_button_rects = []
        
        button_width = 160
        button_height = 40
        button_margin = 10
        
        # Hiển thị các nút thuật toán thành 1 cột
        for i, (name, value) in enumerate(zip(self.algorithm_names, self.algorithm_values)):
            # Tính toán vị trí y dựa trên chỉ số
            y = y_start + i * (button_height + button_margin)
            
            button = pygame.Surface((button_width, button_height))
            button.fill((50, 150, 50) if settings['ai_algorithm'] == value else (100, 100, 100))
            
            # Đặt nút ở bên phải màn hình
            button_rect = button.get_rect(topright=(SCREEN_WIDTH - 20, y))
            
            self.algorithm_buttons.append(button)
            self.algorithm_button_rects.append(button_rect)
            
            self.screen.blit(button, button_rect)
            self.draw_text(name, button_rect.center, 20, WHITE if settings['ai_algorithm'] == value else (220, 220, 220))
        
        # Vẽ nút so sánh thuật toán dưới các nút thuật toán
        last_button_y = y_start + len(self.algorithm_names) * (button_height + button_margin)
        self.compare_algorithms_button_rect = pygame.Rect(SCREEN_WIDTH - 200, last_button_y, 180, 40)
        pygame.draw.rect(self.screen, (100, 150, 200), self.compare_algorithms_button_rect, border_radius=5)
        self.draw_text("So sanh thuat toan", self.compare_algorithms_button_rect.center, 20, WHITE)

    def draw_settings(self, settings):
        pygame.draw.rect(self.screen, (200, 200, 200), pygame.Rect(40, 80, 460, 560), border_radius=10)

        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Cài đặt", True, BLACK)
        title_rect = title.get_rect(center=(270, 50))
        self.screen.blit(title, title_rect)

        pygame.draw.rect(self.screen, (100, 100, 100), self.volume_rect, border_radius=5)
        self.draw_text(f"Am luong: {int(settings['volume'] * 100)}%", self.volume_rect.center, 20)

        pygame.draw.rect(self.screen, (100, 100, 100), self.vibration_rect, border_radius=5)
        self.draw_text(f"Rung: {'BAT' if settings['vibration'] else 'TAT'}", self.vibration_rect.center, 20)

        pygame.draw.rect(self.screen, (100, 100, 100), self.music_rect, border_radius=5)
        self.draw_text(f"NHAC: {'BAT' if settings['music'] else 'TAT'}", self.music_rect.center, 20)
        
        pygame.draw.rect(self.screen, (100, 100, 100), self.ai_mode_rect, border_radius=5)
        self.draw_text(f"Che do AI: {'BAT' if settings['ai_mode'] else 'TAT'}", self.ai_mode_rect.center, 20)

        pygame.draw.rect(self.screen, (100, 100, 100), self.free_movement_rect, border_radius=5)
        self.draw_text(f"Keo tha keo: {'BAT' if settings['free_movement'] else 'TAT'}", self.free_movement_rect.center, 20)

        pygame.draw.rect(self.screen, (100, 100, 100), self.auto_play_rect, border_radius=5)
        self.draw_text(f"Tu dong choi: {'BAT' if settings['auto_play'] else 'TAT'}", self.auto_play_rect.center, 20)

        # Thêm tiêu đề cho phần thuật toán
        algo_title = self.font.render("Thuat toan AI:", True, BLACK)
        algo_title_rect = algo_title.get_rect(topleft=(70, 460))
        self.screen.blit(algo_title, algo_title_rect)

        # Vẽ các nút thuật toán
        self.draw_algorithm_buttons(settings, y_start=490)

        pygame.draw.rect(self.screen, (100, 100, 100), self.back_button_rect, border_radius=5)
        self.draw_text("Quay lai", self.back_button_rect.center, 20)

    def draw_level_select(self, levels, current_level, unlocked_levels):
        self.screen.blit(self.level_select_bg, (0, 0))
        
        title = self.title_font.render("Chon cap do", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 70))
        self.screen.blit(title, title_rect)
        
        self.screen.blit(self.home_button, self.home_button_rect)
        
        self.level_buttons = []
        self.level_button_rects = []
        
        num_levels = len(levels)
        rows = (num_levels + self.max_levels_per_row - 1) // self.max_levels_per_row
        
        for i in range(num_levels):
            row = i // self.max_levels_per_row
            col = i % self.max_levels_per_row
            
            x = SCREEN_WIDTH // 2 + (col - self.max_levels_per_row // 2) * (self.level_button_size + self.level_button_margin)
            if self.max_levels_per_row % 2 == 0:
                x += (self.level_button_size + self.level_button_margin) // 2
            
            y = self.level_button_start_y + row * (self.level_button_size + self.level_button_margin)
            
            level_button = self.level_button.copy()
            level_button_rect = level_button.get_rect(center=(x, y))
            
            if i > unlocked_levels:
                overlay = pygame.Surface((level_button.get_width(), level_button.get_height()), pygame.SRCALPHA)
                overlay.fill((100, 100, 100, 150))
                level_button.blit(overlay, (0, 0))
                
                lock_size = 30
                lock_x = (level_button.get_width() - lock_size) // 2
                lock_y = (level_button.get_height() - lock_size) // 2
                pygame.draw.rect(level_button, WHITE, (lock_x, lock_y, lock_size, lock_size))
                pygame.draw.rect(level_button, BLACK, (lock_x, lock_y, lock_size, lock_size), 2)
                pygame.draw.rect(level_button, BLACK, (lock_x + lock_size // 4, lock_y - lock_size // 4, lock_size // 2, lock_size // 4))
            
            level_text = self.font.render(str(i + 1), True, WHITE)
            level_text_rect = level_text.get_rect(center=(level_button.get_width() // 2, level_button.get_height() // 2))
            level_button.blit(level_text, level_text_rect)
            
            if i == current_level:
                pygame.draw.circle(level_button, (255, 215, 0), (level_button.get_width() // 2, level_button.get_height() // 2), 48, 3)
            
            self.level_buttons.append(level_button)
            self.level_button_rects.append(level_button_rect)
            
            self.screen.blit(level_button, level_button_rect)
            
            level_info = levels[i]
            level_type_text = ""
            if level_info["level_type"] == LevelType.SCORE:
                level_type_text = f"Diem: {level_info['target_score']}"
            elif level_info["level_type"] == LevelType.JELLY:
                level_type_text = "Loai: Keo deo"
            elif level_info["level_type"] == LevelType.INGREDIENT:
                level_type_text = "Loai: Nguyen lieu"
            elif level_info["level_type"] == LevelType.CHOCOLATE:
                level_type_text = "Loai: So-co-la"
            
            info_text = self.small_font.render(level_type_text, True, WHITE)
            info_rect = info_text.get_rect(center=(x, y + self.level_button_size // 2 + 20))
            self.screen.blit(info_text, info_rect)
            
            moves_text = self.small_font.render(f"Luot: {level_info['moves_left']}", True, WHITE)
            moves_rect = moves_text.get_rect(center=(x, y + self.level_button_size // 2 + 40))
            self.screen.blit(moves_text, moves_rect)

    def draw_text(self, text, pos, size=24, color=(0, 0, 0)):
        font = pygame.font.Font(None, size)
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=pos)
        self.screen.blit(surface, rect)

    def show_message(self, message, duration=1000):
        font = pygame.font.SysFont(None, 36)
        text = font.render(message, True, (255, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        padding = 10
        bg_rect = pygame.Rect(text_rect.left - padding, text_rect.top - padding,
                             text_rect.width + 2 * padding, text_rect.height + 2 * padding)
        
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.blit(self.screen, (0, 0), bg_rect)
        
        pygame.draw.rect(self.screen, (255, 255, 255, 200), bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect, 2, border_radius=10)
        self.screen.blit(text, text_rect)
        
        pygame.display.update(bg_rect)
        pygame.time.delay(duration)
        self.screen.blit(bg_surface, bg_rect)
        pygame.display.update(bg_rect)
