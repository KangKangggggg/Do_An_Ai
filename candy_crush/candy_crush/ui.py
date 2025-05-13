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

        # Tải background
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

        # Tải hình nền chọn cấp độ
        try:
            level_select_bg_path = os.path.join(assets_path, "mituot.png")
            if os.path.exists(level_select_bg_path):
                self.level_select_bg = pygame.image.load(level_select_bg_path).convert()
                self.level_select_bg = pygame.transform.scale(self.level_select_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
                print(f"UI: Đã tải hình nền chọn cấp độ từ: {level_select_bg_path}")
            else:
                print(f"UI: Không tìm thấy file mituot.png, tạo hình nền mặc định")
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

        # Tải biểu tượng và nút
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
            level_button_path = os.path.join(assets_path, "level.png")
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

        # Thêm danh sách thuật toán đã chọn để so sánh
        self.selected_algorithms = []

        # Thay đổi nút AI button thành nút Chế độ Thuật Toán
        # self.ai_button = pygame.Surface((120, 40))
        # self.ai_button.fill((100, 150, 200))
        # self.ai_button_rect = self.ai_button.get_rect(topright=(SCREEN_WIDTH - 20, 260))

        # Thay đổi thành:
        self.algorithm_mode_button = pygame.Surface((120, 40))
        self.algorithm_mode_button.fill((100, 150, 200))
        self.algorithm_mode_button_rect = self.algorithm_mode_button.get_rect(topright=(SCREEN_WIDTH - 20, 260))
        
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
        self.compare_algorithms_button_rect = pygame.Rect(SCREEN_WIDTH - 220, 320, 200, 40)  # Đặt nút ở bên phải giao diện chính
        
        # Thêm nút chế độ thuật toán
        self.algorithm_mode_button = pygame.Surface((200, 40))
        self.algorithm_mode_button.fill((100, 150, 200))
        # Đặt các nút thuật toán ở vị trí dễ thấy hơn
        self.algorithm_mode_button_rect = pygame.Rect(
            SCREEN_WIDTH - 250,  # Fixed position from right edge
            SCREEN_HEIGHT - 120,  # Position near bottom of screen
            200, 45  # Slightly larger buttons
        )
        self.compare_algorithms_button_rect = pygame.Rect(
            SCREEN_WIDTH - 250,
            SCREEN_HEIGHT - 65,  # Just below the algorithm mode button
            200, 45
        )
        
        # Thêm các nút thuật toán
        self.algorithm_buttons = []
        self.algorithm_button_rects = []
        self.algorithm_names = ["A*", "BFS", "Backtracking", "Simulated Annealing", "Q-Learning", "And-Or"]
        self.algorithm_values = ["a_star", "bfs", "backtracking", "simulated_annealing", "q_learning", "and_or"]

        # Thêm nút tạm dừng trò chơi
        self.pause_button = pygame.Surface((200, 40))
        self.pause_button.fill((200, 100, 100))
        self.pause_button_rect = pygame.Rect(SCREEN_WIDTH - 220, 380, 200, 40)  # Đặt nút dưới nút so sánh thuật toán
        
        # Thêm nút tiếp tục trò chơi
        self.resume_button = pygame.Surface((200, 40))
        self.resume_button.fill((100, 200, 100))
        self.resume_button_rect = pygame.Rect(SCREEN_WIDTH - 220, 380, 200, 40)  # Cùng vị trí với nút tạm dừng
        
        # Thêm nút menu level
        self.menu_level_button = pygame.Surface((200, 40))
        self.menu_level_button.fill((150, 150, 200))
        self.menu_level_button_rect = pygame.Rect(SCREEN_WIDTH - 220, 440, 200, 40)  # Đặt dưới nút tạm dừng/tiếp tục
        
        # Thêm nút chế độ thuật toán và so sánh thuật toán cho giao diện next level
        self.next_level_algorithm_mode_button = pygame.Surface((200, 40))
        self.next_level_algorithm_mode_button.fill((100, 150, 200))
        self.next_level_algorithm_mode_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 80, 200, 40)

        self.next_level_compare_algorithms_button = pygame.Surface((200, 40))
        self.next_level_compare_algorithms_button.fill((100, 150, 200))
        self.next_level_compare_algorithms_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 130, 200, 40)

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
                
                # Vẽ nút Chế độ Thuật Toán với thiết kế đơn giản
                if self.algorithm_mode_button and self.algorithm_mode_button_rect:
                    # Draw simple blue button
                    pygame.draw.rect(self.screen, (100, 149, 237), self.algorithm_mode_button_rect)
                    
                    # Draw text
                    self.draw_text("Chế độ Thuật Toán", 
                                  self.algorithm_mode_button_rect.center, 
                                  20, WHITE)
                
                # Vẽ nút so sánh thuật toán với thiết kế đơn giản
                pygame.draw.rect(self.screen, (100, 149, 237), self.compare_algorithms_button_rect)
                
                # Draw text
                self.draw_text("So sánh thuật toán", 
                              self.compare_algorithms_button_rect.center, 
                              20, WHITE)

                # Vẽ nút tạm dừng hoặc tiếp tục trò chơi
                if hasattr(self, 'pause_button') and hasattr(self, 'resume_button'):
                    if settings.get('ai_mode', False):  # Chỉ hiển thị khi chế độ AI được bật
                        if not getattr(settings, 'game_paused', False):
                            pygame.draw.rect(self.screen, (200, 100, 100), self.pause_button_rect, border_radius=5)
                            self.draw_text("Tam dung tro choi", self.pause_button_rect.center, 20, WHITE)
                        else:
                            pygame.draw.rect(self.screen, (100, 200, 100), self.resume_button_rect, border_radius=5)
                            self.draw_text("Tiep tuc tro choi", self.resume_button_rect.center, 20, WHITE)

                # Vẽ nút menu level
                pygame.draw.rect(self.screen, (150, 150, 200), self.menu_level_button_rect, border_radius=5)
                self.draw_text("Menu Level", self.menu_level_button_rect.center, 20, WHITE)

                # Thêm thông báo nhỏ bên dưới nút so sánh thuật toán
                if level_number == 1:
                    note_font = pygame.font.SysFont(None, 16)
                    note_text = "Hoan thanh level 1 de so sanh"
                    note_surface = note_font.render(note_text, True, (255, 255, 200))
                    note_rect = note_surface.get_rect(center=(self.compare_algorithms_button_rect.centerx, self.compare_algorithms_button_rect.bottom + 10))
                    self.screen.blit(note_surface, note_rect)

        if self.game_state in (GameState.LEVEL_COMPLETE, GameState.GAME_OVER):
            self.screen.blit(self.play_button, self.play_button_rect)

    # Fix the algorithm buttons drawing
    def draw_algorithm_buttons(self, settings, y_start=260):
        """Vẽ các nút thuật toán trong chế độ thuật toán"""
        self.algorithm_buttons = []
        self.algorithm_button_rects = []
        
        # Tạo overlay cho chế độ thuật toán
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Tạo panel cho các nút thuật toán
        panel_width = 500
        panel_height = 550
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        pygame.draw.rect(self.screen, (240, 240, 240), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        border_radius=15)
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        2, border_radius=15)
        
        # Tiêu đề
        title_font = pygame.font.SysFont(None, 40)
        title = title_font.render("Chon thuat toan AI", True, (0, 0, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 30))
        self.screen.blit(title, title_rect)
        
        # Hướng dẫn
        guide_font = pygame.font.SysFont(None, 24)
        guide_text1 = guide_font.render("Nhan de chon thuat toan", True, (0, 0, 0))
        guide_text2 = guide_font.render("Nhan them lan nua de them vao danh sach", True, (0, 0, 0))
        guide_rect1 = guide_text1.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 60))
        guide_rect2 = guide_text2.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 85))
        self.screen.blit(guide_text1, guide_rect1)
        self.screen.blit(guide_text2, guide_rect2)
        
        # Vẽ đường kẻ phân cách
        pygame.draw.line(self.screen, (150, 150, 150), 
                        (panel_x + 50, panel_y + 110), 
                        (panel_x + panel_width - 50, panel_y + 110), 
                        2)
        
        button_width = 400
        button_height = 50
        button_margin = 15
        
        # Hiển thị các nút thuật toán trong panel
        for i, (name, value) in enumerate(zip(self.algorithm_names, self.algorithm_values)):
            # Tính toán vị trí y dựa trên chỉ số
            y = panel_y + 130 + i * (button_height + button_margin)
            
            # Xác định màu nút dựa trên trạng thái
            if settings['ai_algorithm'] == value:
                button_color = (50, 150, 50)  # Màu xanh lá cho thuật toán đang được chọn
                text_color = WHITE
                status_text = "Dang su dung"
            elif value in self.selected_algorithms:
                button_color = (150, 150, 50)  # Màu vàng cho thuật toán được chọn để so sánh
                text_color = WHITE
                status_text = "Da chon so sanh"
            else:
                button_color = (100, 100, 200)  # Màu xanh dương cho các thuật toán khác
                text_color = WHITE
                status_text = "Nhan de chon"
            
            # Vẽ nút với viền bo tròn
            button_rect = pygame.Rect(panel_x + (panel_width - button_width) // 2, y, button_width, button_height)
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
            
            # Vẽ viền
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=10)
            
            self.algorithm_button_rects.append(button_rect)
            
            # Vẽ tên thuật toán
            algorithm_name_font = pygame.font.SysFont(None, 28)
            algorithm_name_text = algorithm_name_font.render(name, True, text_color)
            algorithm_name_rect = algorithm_name_text.get_rect(midleft=(button_rect.x + 20, button_rect.y + button_rect.height // 2))
            self.screen.blit(algorithm_name_text, algorithm_name_rect)
            
            # Vẽ trạng thái
            status_font = pygame.font.SysFont(None, 20)
            status_surface = status_font.render(status_text, True, text_color)
            status_rect = status_surface.get_rect(midright=(button_rect.right - 20, button_rect.y + button_rect.height // 2))
            self.screen.blit(status_surface, status_rect)
        
        # Hiển thị thuật toán đã chọn
        if len(self.selected_algorithms) > 0:
            selected_text = pygame.font.SysFont(None, 20).render(
                f"Da chon: {', '.join(self.selected_algorithms)}", True, (0, 0, 0))
            selected_rect = selected_text.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 130))
            self.screen.blit(selected_text, selected_rect)
        
        # Nút so sánh thuật toán (chỉ hiển thị khi có ít nhất 2 thuật toán được chọn)
        # Di chuyển nút so sánh xuống dưới, không còn ở giữa các nút thuật toán
        if len(self.selected_algorithms) >= 2:
            info_text = pygame.font.SysFont(None, 20).render(
                "", True, (0, 0, 0))
            info_rect = info_text.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 120))
            self.screen.blit(info_text, info_rect)
        
        # Nút đóng
        close_button_width = 150
        close_button_height = 50
        close_button_x = panel_x + (panel_width - close_button_width) // 2
        close_button_y = panel_y + panel_height - 60
        close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_width, close_button_height)
        
        # Vẽ nút với viền bo tròn
        pygame.draw.rect(self.screen, (200, 100, 100), close_button_rect, border_radius=10)
        
        # Vẽ viền
        pygame.draw.rect(self.screen, (150, 50, 50), close_button_rect, 2, border_radius=10)
        
        close_text = pygame.font.SysFont(None, 28).render("Dong", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=close_button_rect.center)
        self.screen.blit(close_text, close_text_rect)
        
        # Lưu rect của nút đóng để xử lý sự kiện
        self.close_algorithm_button_rect = close_button_rect

    def draw_settings(self, settings):
        # Tạo lớp phủ bán trong suốt
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Tạo panel cho cài đặt
        panel_width = 500
        panel_height = 500  # Tăng chiều cao để thêm nút âm thanh hiệu ứng
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Vẽ panel chính với góc bo tròn
        pygame.draw.rect(self.screen, (220, 220, 220), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        2, border_radius=15)

        # Tiêu đề với kiểu dáng đẹp hơn
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Cai dat", True, (50, 50, 50))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # Đường phân cách
        pygame.draw.line(self.screen, (150, 150, 150), 
                        (panel_x + 50, panel_y + 80), 
                        (panel_x + panel_width - 50, panel_y + 80), 
                        2)

        # Thiết kế lại các nút với kiểu dáng đẹp hơn
        button_width = 300
        button_height = 60
        button_margin = 30  # Tăng khoảng cách giữa các nút
        button_x = panel_x + (panel_width - button_width) // 2
        
        # Nút âm lượng
        volume_y = panel_y + 120
        self.volume_rect = pygame.Rect(button_x, volume_y, button_width, button_height)
        pygame.draw.rect(self.screen, (100, 100, 100), self.volume_rect, border_radius=10)
        self.draw_text(f"Am luong: {int(settings['volume'] * 100)}%", self.volume_rect.center, 24, (255, 255, 255))
        
        # Nút nhạc - đặt ngay dưới nút volume
        music_y = volume_y + button_height + button_margin
        self.music_rect = pygame.Rect(button_x, music_y, button_width, button_height)
        pygame.draw.rect(self.screen, (100, 100, 100), self.music_rect, border_radius=10)
        self.draw_text(f"NHAC: {'BAT' if settings['music'] else 'TAT'}", self.music_rect.center, 24, (255, 255, 255))
        
        # Nút âm thanh hiệu ứng - thêm mới
        sound_effects_y = music_y + button_height + button_margin
        self.sound_effects_rect = pygame.Rect(button_x, sound_effects_y, button_width, button_height)
        pygame.draw.rect(self.screen, (100, 100, 100), self.sound_effects_rect, border_radius=10)
        self.draw_text(f"HIEU UNG AM THANH: {'BAT' if settings.get('sound_effects', True) else 'TAT'}", self.sound_effects_rect.center, 24, (255, 255, 255))
        
        # Nút quay lại
        back_y = panel_y + panel_height - 80
        self.back_button_rect = pygame.Rect(button_x, back_y, button_width, button_height)
        pygame.draw.rect(self.screen, (100, 100, 100), self.back_button_rect, border_radius=10)
        self.draw_text("Quay lai", self.back_button_rect.center, 24, (255, 255, 255))
        
        # Thêm biểu tượng để có gợi ý trực quan hơn
        # Biểu tượng âm lượng
        volume_icon_x = button_x + 30
        pygame.draw.rect(self.screen, (255, 255, 255), (volume_icon_x, volume_y + 20, 10, 20), border_radius=3)
        pygame.draw.arc(self.screen, (255, 255, 255), (volume_icon_x + 15, volume_y + 15, 15, 30), -0.5, 0.5, 2)
        pygame.draw.arc(self.screen, (255, 255, 255), (volume_icon_x + 20, volume_y + 10, 20, 40), -0.5, 0.5, 2)
        
        # Biểu tượng nhạc
        music_icon_x = button_x + 30
        pygame.draw.rect(self.screen, (255, 255, 255), (music_icon_x, music_y + 20, 5, 20), border_radius=2)
        pygame.draw.rect(self.screen, (255, 255, 255), (music_icon_x + 10, music_y + 15, 5, 25), border_radius=2)
        pygame.draw.rect(self.screen, (255, 255, 255), (music_icon_x + 20, music_y + 10, 5, 30), border_radius=2)
        pygame.draw.rect(self.screen, (255, 255, 255), (music_icon_x + 30, music_y + 15, 5, 25), border_radius=2)
        
        # Biểu tượng âm thanh hiệu ứng
        sound_effects_icon_x = button_x + 30
        pygame.draw.circle(self.screen, (255, 255, 255), (sound_effects_icon_x + 15, sound_effects_y + 30), 10, 2)
        pygame.draw.circle(self.screen, (255, 255, 255), (sound_effects_icon_x + 15, sound_effects_y + 30), 15, 1)
        pygame.draw.circle(self.screen, (255, 255, 255), (sound_effects_icon_x + 15, sound_effects_y + 30), 20, 1)

    def draw_level_select(self, levels, current_level, unlocked_levels):
        self.screen.blit(self.level_select_bg, (0, 0))
        
        title = self.title_font.render("Chon cap do", True, BLACK)
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
            
            # Căn giữa các nút theo chiều ngang
            total_width = self.max_levels_per_row * self.level_button_size + (self.max_levels_per_row - 1) * self.level_button_margin
            start_x = (SCREEN_WIDTH - total_width) // 2
            x = start_x + col * (self.level_button_size + self.level_button_margin) + self.level_button_size // 2
            
            y = self.level_button_start_y + row * (self.level_button_size + self.level_button_margin)
            
            level_button = self.level_button.copy()
            level_button_rect = level_button.get_rect(center=(x, y))
            
            # Nếu cấp độ bị khóa, thêm lớp phủ và biểu tượng khóa
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
            
            # Nếu là cấp độ hiện tại, thêm vòng tròn vàng
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
            
            info_text = self.small_font.render(level_type_text, True, BLACK)
            info_rect = info_text.get_rect(center=(x, y + self.level_button_size // 2 + 20))
            self.screen.blit(info_text, info_rect)
            
            moves_text = self.small_font.render(f"Luot: {level_info['moves_left']}", True, BLACK)
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
