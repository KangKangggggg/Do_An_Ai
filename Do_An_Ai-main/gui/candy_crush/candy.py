import pygame
import random
import os
from constants import *

# Load ảnh kẹo
try:
    CANDY_IMAGES = {
        "RED": pygame.image.load(r"D:\Downloads\Do_An_Ai-main\Do_An_Ai-main\assets\candy_red.png"),
        "GREEN": pygame.image.load(r"D:\Downloads\Do_An_Ai-main\Do_An_Ai-main\assets\candy_green.png"),
        "BLUE": pygame.image.load(r"D:\Downloads\Do_An_Ai-main\Do_An_Ai-main\assets\candy_blue.png"),
        "YELLOW": pygame.image.load(r"D:\Downloads\Do_An_Ai-main\Do_An_Ai-main\assets\candy_yellow.png"),
        "ORANGE": pygame.image.load(r"D:\Downloads\Do_An_Ai-main\Do_An_Ai-main\assets\candy_orange.png"),
        "VIOLET": pygame.image.load(r"D:\Downloads\Do_An_Ai-main\Do_An_Ai-main\assets\candy_violet.png"),
    }
except pygame.error:
    # Nếu không tìm thấy ảnh, sử dụng màu thay thế
    print("Không thể tải ảnh kẹo. Sử dụng màu thay thế.")
    CANDY_IMAGES = {}

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
        self.blocker_type = BlockerType.NONE
        self.blocker_health = 0

    def update(self):
        # Kiểm tra xem kẹo có cần di chuyển không
        if self.x != self.target_x or self.y != self.target_y:
            self.moving = True
            # Tính toán khoảng cách di chuyển
            dx = (self.target_x - self.x) / 5
            dy = (self.target_y - self.y) / 5
            
            # Di chuyển kẹo
            if abs(dx) < 1:
                self.x = self.target_x
            else:
                self.x += dx
                
            if abs(dy) < 1:
                self.y = self.target_y
            else:
                self.y += dy
                
            # Kiểm tra xem đã đến đích chưa
            if self.x == self.target_x and self.y == self.target_y:
                self.moving = False
        else:
            self.moving = False

    def draw(self, screen):
        # Vẽ nền jelly nếu cần
        if self.jelly:
            jelly_color = (255, 100, 255, 128)
            jelly_rect = pygame.Rect(self.x + 5, self.y + 5, CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(screen, jelly_color, jelly_rect, border_radius=10)
            if self.double_jelly:
                pygame.draw.rect(screen, (200, 0, 200), jelly_rect, 3, border_radius=10)

        # Vẽ chocolate
        if self.chocolate:
            chocolate_rect = pygame.Rect(self.x + 5, self.y + 5, CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(screen, BROWN, chocolate_rect, border_radius=5)
            return

        # Vẽ ingredient
        if self.ingredient:
            pygame.draw.circle(screen, (139, 69, 19), (int(self.x + CELL_SIZE//2), int(self.y + CELL_SIZE//2)), CELL_SIZE//3)
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x + CELL_SIZE//2), int(self.y + CELL_SIZE//3)), CELL_SIZE//6)
            return

        # Vẽ kẹo bằng ảnh
        img_key = self.candy_type.name
        if img_key in CANDY_IMAGES:
            img = pygame.transform.scale(CANDY_IMAGES[img_key], (CELL_SIZE, CELL_SIZE))
            screen.blit(img, (int(self.x), int(self.y)))
        else:
            # Dự phòng: vẽ hình tròn với màu tương ứng
            pygame.draw.circle(screen, self.get_color(),
                              (int(self.x + CELL_SIZE//2), int(self.y + CELL_SIZE//2)),
                              CELL_SIZE//2 - 5)
                    
        # Vẽ đặc điểm kẹo đặc biệt
        if self.special_type == SpecialType.STRIPED_H:
            for i in range(3):
                y_pos = self.y + (CELL_SIZE//4) * (i + 1)
                pygame.draw.line(screen, WHITE, (self.x + 10, y_pos), (self.x + CELL_SIZE - 10, y_pos), 3)
        elif self.special_type == SpecialType.STRIPED_V:
            for i in range(3):
                x_pos = self.x + (CELL_SIZE//4) * (i + 1)
                pygame.draw.line(screen, WHITE, (x_pos, self.y + 10), (x_pos, self.y + CELL_SIZE - 10), 3)
        elif self.special_type == SpecialType.WRAPPED:
            pygame.draw.rect(screen, WHITE, (self.x + CELL_SIZE//4, self.y + CELL_SIZE//4, CELL_SIZE//2, CELL_SIZE//2), 3)
            if not self.remove:
                for i in range(8):
                    angle = i*45 + (pygame.time.get_ticks()//50) % 45
                    start_x, start_y = self.x + CELL_SIZE//2, self.y + CELL_SIZE//2
                    end_x = start_x + int((CELL_SIZE//2 + 5) * pygame.math.Vector2(1,0).rotate(angle).x)
                    end_y = start_y + int((CELL_SIZE//2 + 5) * pygame.math.Vector2(1,0).rotate(angle).y)
                    pygame.draw.line(screen, (255,255,0), (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)
        elif self.special_type == SpecialType.COLOR_BOMB:
            pygame.draw.circle(screen, BLACK, (int(self.x + CELL_SIZE//2), int(self.y + CELL_SIZE//2)), CELL_SIZE//2 - 5)
            for i in range(8):
                angle = i*45 + (pygame.time.get_ticks()//100) % 45
                start_x, start_y = self.x + CELL_SIZE//2, self.y + CELL_SIZE//2
                end_x = start_x + int((CELL_SIZE//2 - 8) * pygame.math.Vector2(1,0).rotate(angle).x)
                end_y = start_y + int((CELL_SIZE//2 - 8) * pygame.math.Vector2(1,0).rotate(angle).y)
                color = self.get_color_by_type(CandyType((i + (pygame.time.get_ticks()//500)) % 6))
                pygame.draw.line(screen, color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), 3)
            pygame.draw.circle(screen, WHITE, (int(self.x + CELL_SIZE//2), int(self.y + CELL_SIZE//2)), 4)

        # Vẽ blocker nếu có
        if self.blocker_type != BlockerType.NONE:
            # Bạn có thể giữ nguyên logic blocker ở đây
            pass

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
        elif candy_type == CandyType.VIOLET:
            return VIOLET
        elif candy_type == CandyType.ORANGE:
            return ORANGE
        return WHITE
