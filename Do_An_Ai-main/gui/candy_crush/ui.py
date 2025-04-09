import pygame
from constants import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 72)
        self.game_state = GameState.MENU  # Thêm biến lưu trạng thái game

        # Load ảnh nền
        self.background_image = pygame.image.load(r"D:\Downloads\Do_An_Ai-main\Do_An_Ai-main\assets\level1.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Load ảnh nút cài đặt
        self.settings_icon = pygame.image.load(r"D:\Downloads\Do_An_Ai-main\Do_An_Ai-main\assets\button_hover.png").convert_alpha()
        self.settings_icon = pygame.transform.scale(self.settings_icon, (60, 60))  # Kích thước mong muốn
        self.settings_rect = self.settings_icon.get_rect()
        self.settings_rect.topright = (SCREEN_WIDTH - 20, 100 + 40)  # Dưới thanh mục tiêu một chút
        
        # Load ảnh nút play
        self.play_button = pygame.image.load(r"D:\Downloads\Do_An_Ai-main\Do_An_Ai-main\assets\button.png").convert_alpha()
        self.play_button = pygame.transform.scale(self.play_button, (120, 50))  # Kích thước mong muốn
        self.play_button_rect = self.play_button.get_rect()
        self.play_button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)  # Đặt ở dưới màn hình

    def draw_grid(self):
        # Vẽ ảnh nền
        self.screen.blit(self.background_image, (0, 0))
        
        # Tạo lớp phủ mờ màu trắng (hoặc màu khác tùy bạn)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 150))  # RGBA – A=150 là độ mờ (0 là trong suốt, 255 là đục)
        self.screen.blit(overlay, (0, 0))

        # Vẽ nền lưới
        grid_rect = pygame.Rect(GRID_OFFSET_X - 5, GRID_OFFSET_Y - 5, 
                                GRID_SIZE * CELL_SIZE + 10, GRID_SIZE * CELL_SIZE + 10)
        pygame.draw.rect(self.screen, GRAY, grid_rect, border_radius=10)

        # Vẽ lưới
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, BLACK, 
                            (GRID_OFFSET_X, GRID_OFFSET_Y + i * CELL_SIZE),
                            (GRID_OFFSET_X + GRID_SIZE * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE), 1)
            pygame.draw.line(self.screen, BLACK, 
                            (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y),
                            (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE), 1)

    
    def draw_selection(self, row, col):
        rect = pygame.Rect(GRID_OFFSET_X + col * CELL_SIZE + 2, GRID_OFFSET_Y + row * CELL_SIZE + 2, 
                          CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.rect(self.screen, (255, 255, 0), rect, 3, border_radius=5)
    
    def draw_level_info(self, level_number, score, moves_left, level_type, target_score=0, 
                       jellies_left=0, ingredients_left=0, chocolates_left=0, blockers_count=0):
        # Vẽ thông tin cấp độ
        level_text = self.font.render(f"Cấp độ {level_number}", True, BLACK)
        self.screen.blit(level_text, (20, 20))
        
        # Vẽ điểm số
        score_text = self.font.render(f"Điểm: {score}", True, BLACK)
        self.screen.blit(score_text, (20, 60))
        
        # Vẽ số lượt đi còn lại
        moves_text = self.font.render(f"Lượt: {moves_left}", True, BLACK)
        self.screen.blit(moves_text, (20, 100))
        
        # Vẽ số lượng nút chặn
        if blockers_count > 0:
            blockers_text = self.font.render(f"Nút chặn: {blockers_count}", True, (100, 100, 100))
            self.screen.blit(blockers_text, (SCREEN_WIDTH - 200, 100))
        
        # Load ảnh nút cài đặt
        self.settings_img = pygame.image.load(r"D:\Downloads\Do_An_Ai-main\Do_An_Ai-main\assets\button_hover.png").convert_alpha()
        self.settings_img = pygame.transform.scale(self.settings_img, (50, 50))  # resize nếu cần

        # Trong draw_level_info cuối hàm:
        self.settings_rect = self.settings_img.get_rect()
        self.settings_rect.topleft = (SCREEN_WIDTH - 80, 90)  # vị trí dưới thanh mục tiêu
        self.screen.blit(self.settings_img, self.settings_rect)


        # Vẽ mục tiêu cấp độ
        if level_type == LevelType.SCORE:
            objective_text = self.font.render(f"Mục tiêu: {target_score}", True, BLACK)
            self.screen.blit(objective_text, (SCREEN_WIDTH - 200, 20))
            
            # Vẽ thanh tiến trình
            progress = min(1.0, score / target_score) if target_score > 0 else 0
            bar_width = 180
            pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH - 200, 60, bar_width, 20), border_radius=5)
            pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 200, 60, int(bar_width * progress), 20), border_radius=5)
            
        elif level_type == LevelType.JELLY:
            objective_text = self.font.render(f"Kẹo dẻo: {jellies_left}", True, PINK)
            self.screen.blit(objective_text, (SCREEN_WIDTH - 200, 20))
            
        elif level_type == LevelType.INGREDIENTS:
            objective_text = self.font.render(f"Nguyên liệu: {ingredients_left}", True, BROWN)
            self.screen.blit(objective_text, (SCREEN_WIDTH - 200, 20))
            
        elif level_type == LevelType.CHOCOLATE:
            objective_text = self.font.render(f"Sô-cô-la: {chocolates_left}", True, BROWN)
            self.screen.blit(objective_text, (SCREEN_WIDTH - 200, 20))
        
        # Hiển thị nút cài đặt
        self.screen.blit(self.settings_icon, self.settings_rect)
        
        # Hiển thị nút play chỉ khi ở trạng thái kết thúc cấp độ hoặc game over
        if self.game_state == GameState.LEVEL_COMPLETE or self.game_state == GameState.GAME_OVER:
            self.play_button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
            self.screen.blit(self.play_button, self.play_button_rect)
    
    def draw_message(self, title, subtitle):
        # Vẽ lớp phủ bán trong suốt
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Vẽ tiêu đề
        title_text = self.title_font.render(title, True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(title_text, title_rect)
        
        # Vẽ phụ đề
        subtitle_text = self.font.render(subtitle, True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(subtitle_text, subtitle_rect)

    # Thêm phương thức draw_menu vào class UI
    def draw_menu(self):
        # Vẽ ảnh nền
        self.screen.blit(self.background_image, (0, 0))
        
        # Tạo lớp phủ mờ màu trắng
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))  # RGBA – A=180 là độ mờ
        self.screen.blit(overlay, (0, 0))
        
        # Vẽ tiêu đề trò chơi
        title_text = self.title_font.render("Candy Crush", True, (220, 20, 60))  # Màu đỏ tươi
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title_text, title_rect)
        
        # Vẽ nút play ở giữa màn hình
        play_button_center = self.play_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.play_button_rect = play_button_center
        self.screen.blit(self.play_button, self.play_button_rect)
        
        # Vẽ hướng dẫn
        instruction_text = self.font.render("Nhấn nút Play để bắt đầu trò chơi", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
        self.screen.blit(instruction_text, instruction_rect)
