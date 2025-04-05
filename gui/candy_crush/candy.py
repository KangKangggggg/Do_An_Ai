import pygame
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
            pygame.draw.rect(screen, WHITE, (self.x + CELL_SIZE // 4, self.y + CELL_SIZE // 4, 
                                            CELL_SIZE // 2, CELL_SIZE // 2), 3)
        
        elif self.special_type == SpecialType.COLOR_BOMB:
            pygame.draw.circle(screen, BLACK, (self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2), CELL_SIZE // 2 - 5)
            for i in range(6):
                angle = i * 60
                rad = angle * 3.14159 / 180
                start_x = self.x + CELL_SIZE // 2
                start_y = self.y + CELL_SIZE // 2
                end_x = start_x + int((CELL_SIZE // 2 - 8) * pygame.math.Vector2(1, 0).rotate(angle).x)
                end_y = start_y + int((CELL_SIZE // 2 - 8) * pygame.math.Vector2(1, 0).rotate(angle).y)
                color = self.get_color_by_type(CandyType(i % 6))
                pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 3)
    
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