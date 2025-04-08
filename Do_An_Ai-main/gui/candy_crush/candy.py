import pygame
import random
from constants import *

class Candy:
    def __init__(self, row, col, candy_type):
        self.row = row
        self.col = col
        self.candy_type = candy_type
        self.special_type = SpecialType.NORMAL
        self.x = GRID_OFFSET_X + col * CELL_SIZE
        self.y = GRID_OFFSET_Y + row * CELL_SIZE
        self.target_x = self.x
        self.target_y = self.y
        self.moving = False
        self.remove = False
        self.jelly = False
        self.double_jelly = False
        self.chocolate = False
        self.ingredient = False
        
        # Thuộc tính cho các nút chặn
        self.blocker_type = BlockerType.NONE
        self.blocker_health = 0  # Số lần cần khớp để phá hủy

    def update(self):
        # Di chuyển kẹo đến vị trí đích
        if self.x != self.target_x or self.y != self.target_y:
            self.moving = True
            dx = (self.target_x - self.x) / 5
            dy = (self.target_y - self.y) / 5
            
            if abs(dx) < 1:
                self.x = self.target_x
            else:
                self.x += dx
                
            if abs(dy) < 1:
                self.y = self.target_y
            else:
                self.y += dy
                
            if self.x == self.target_x and self.y == self.target_y:
                self.moving = False
        else:
            self.moving = False

    def draw(self, screen):
        # Vẽ kẹo
        color = self.get_color()
        
        # Vẽ nền kẹo dẻo nếu cần
        if self.jelly:
            jelly_color = (255, 100, 255, 128)
            jelly_rect = pygame.Rect(self.x + 5, self.y + 5, CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(screen, jelly_color, jelly_rect, border_radius=10)
            
            if self.double_jelly:
                pygame.draw.rect(screen, (200, 0, 200), jelly_rect, 3, border_radius=10)
        
        # Vẽ sô-cô-la
        if self.chocolate:
            chocolate_rect = pygame.Rect(self.x + 5, self.y + 5, CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(screen, BROWN, chocolate_rect, border_radius=5)
            return
            
        # Vẽ nguyên liệu
        if self.ingredient:
            pygame.draw.circle(screen, (139, 69, 19), (self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2), CELL_SIZE // 3)
            pygame.draw.circle(screen, (255, 0, 0), (self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 3), CELL_SIZE // 6)
            return
        
        # Vẽ kẹo thường
        pygame.draw.circle(screen, color, (self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2), CELL_SIZE // 2 - 5)
        
        # Vẽ các đặc điểm của kẹo đặc biệt
        if self.special_type == SpecialType.STRIPED_H:
            for i in range(3):
                y_pos = self.y + (CELL_SIZE // 4) * (i + 1)
                pygame.draw.line(screen, WHITE, (self.x + 10, y_pos), (self.x + CELL_SIZE - 10, y_pos), 3)
        
        elif self.special_type == SpecialType.STRIPED_V:
            for i in range(3):
                x_pos = self.x + (CELL_SIZE // 4) * (i + 1)
                pygame.draw.line(screen, WHITE, (x_pos, self.y + 10), (x_pos, self.y + CELL_SIZE - 10), 3)
        
        elif self.special_type == SpecialType.WRAPPED:
            # Vẽ kẹo bọc
            pygame.draw.rect(screen, WHITE, (self.x + CELL_SIZE // 4, self.y + CELL_SIZE // 4, 
                                            CELL_SIZE // 2, CELL_SIZE // 2), 3)
            
            # Hiệu ứng lấp lánh xung quanh kẹo bọc
            if not self.remove:  # Chỉ hiển thị hiệu ứng nếu kẹo không bị đánh dấu xóa
                for i in range(8):
                    angle = i * 45 + (pygame.time.get_ticks() // 50) % 45
                    start_x = self.x + CELL_SIZE // 2
                    start_y = self.y + CELL_SIZE // 2
                    end_x = start_x + int((CELL_SIZE // 2 + 5) * pygame.math.Vector2(1, 0).rotate(angle).x)
                    end_y = start_y + int((CELL_SIZE // 2 + 5) * pygame.math.Vector2(1, 0).rotate(angle).y)
                    pygame.draw.line(screen, (255, 255, 0), (start_x, start_y), (end_x, end_y), 2)
        
        elif self.special_type == SpecialType.COLOR_BOMB:
            # Vẽ kẹo màu (bom màu)
            # Vẽ nền đen
            pygame.draw.circle(screen, BLACK, (self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2), CELL_SIZE // 2 - 5)
            
            # Vẽ các tia màu sắc
            for i in range(8):
                angle = i * 45 + (pygame.time.get_ticks() // 100) % 45  # Hiệu ứng xoay
                start_x = self.x + CELL_SIZE // 2
                start_y = self.y + CELL_SIZE // 2
                end_x = start_x + int((CELL_SIZE // 2 - 8) * pygame.math.Vector2(1, 0).rotate(angle).x)
                end_y = start_y + int((CELL_SIZE // 2 - 8) * pygame.math.Vector2(1, 0).rotate(angle).y)
                
                # Màu sắc thay đổi theo thời gian
                color_index = (i + (pygame.time.get_ticks() // 500)) % 6
                color = self.get_color_by_type(CandyType(color_index))
                
                pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 3)
            
            # Vẽ điểm trắng ở giữa
            pygame.draw.circle(screen, WHITE, (self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2), 4)
        
        # Vẽ các nút chặn
        if self.blocker_type != BlockerType.NONE:
            if self.blocker_type == BlockerType.ICE:
                # Vẽ khối băng
                ice_rect = pygame.Rect(self.x, self.y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, LIGHT_BLUE, ice_rect, border_radius=5)
                
                # Vẽ đường viền và hiệu ứng băng
                pygame.draw.rect(screen, WHITE, ice_rect, 2, border_radius=5)
                
                # Vẽ các đường nứt nếu là lớp băng thứ hai
                if self.blocker_health == 1:
                    for i in range(3):
                        start_x = self.x + random.randint(5, CELL_SIZE - 5)
                        start_y = self.y + random.randint(5, CELL_SIZE - 5)
                        end_x = start_x + random.randint(-10, 10)
                        end_y = start_y + random.randint(-10, 10)
                        pygame.draw.line(screen, WHITE, (start_x, start_y), (end_x, end_y), 1)
            
            elif self.blocker_type == BlockerType.STONE:
                # Vẽ khối đá
                stone_rect = pygame.Rect(self.x + 2, self.y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                pygame.draw.rect(screen, GRAY, stone_rect, border_radius=5)
                
                # Vẽ hiệu ứng đá
                for i in range(4):
                    circle_x = self.x + 10 + i * 12
                    circle_y = self.y + 10 + (i % 2) * 12
                    pygame.draw.circle(screen, (150, 150, 150), (circle_x, circle_y), 3)
            
            elif self.blocker_type == BlockerType.LOCK:
                # Vẽ khối khóa
                lock_rect = pygame.Rect(self.x + 5, self.y + 5, CELL_SIZE - 10, CELL_SIZE - 10)
                pygame.draw.rect(screen, (200, 200, 100), lock_rect, border_radius=5)
                
                # Vẽ hình khóa
                lock_body = pygame.Rect(self.x + CELL_SIZE//2 - 7, self.y + CELL_SIZE//2, 14, 15)
                pygame.draw.rect(screen, (150, 150, 50), lock_body, border_radius=3)
                
                # Vẽ phần trên của khóa
                lock_top = pygame.Rect(self.x + CELL_SIZE//2 - 10, self.y + CELL_SIZE//2 - 10, 20, 15)
                pygame.draw.arc(screen, (150, 150, 50), lock_top, 3.14, 0, 3)
            
            elif self.blocker_type == BlockerType.LICORICE:
                # Vẽ khối kẹo cứng
                licorice_rect = pygame.Rect(self.x + 2, self.y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                pygame.draw.rect(screen, (50, 50, 50), licorice_rect, border_radius=8)
                
                # Vẽ các đường sọc
                for i in range(3):
                    y_pos = self.y + 10 + i * 15
                    pygame.draw.line(screen, (100, 100, 100), (self.x + 10, y_pos), (self.x + CELL_SIZE - 10, y_pos), 2)
    
    def get_color(self):
        return self.get_color_by_type(self.candy_type)
    
    def get_color_by_type(self, candy_type):
        if candy_type == CandyType.RED:
            return RED
        elif candy_type == CandyType.GREEN:
            return GREEN
        elif candy_type == CandyType.BLUE:
            return BLUE
        elif candy_type == CandyType.YELLOW:
            return YELLOW
        elif candy_type == CandyType.PURPLE:
            return PURPLE
        elif candy_type == CandyType.ORANGE:
            return ORANGE
        return WHITE
