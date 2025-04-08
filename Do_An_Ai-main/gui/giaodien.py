import pygame
import random
import sys
import os
import math
from pygame.locals import *
from typing import List, Tuple, Dict, Optional, Set

# Khởi tạo pygame
pygame.init()
pygame.mixer.init()

# Các hằng số
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 900
BOARD_SIZE = 8

CELL_SIZE = 80
MARGIN = 50
FPS = 60
ANIMATION_SPEED = 10

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (204, 153, 255)  # Màu tím nhạt
GRID_COLOR = (255, 192, 203)       # Màu hồng nhạt
TEXT_COLOR = (139, 0, 139)         # Màu tím đậm
BUTTON_COLOR = (50, 205, 50)       # Màu xanh lá cho nút Play
BUTTON_EXIT_COLOR = (255, 105, 180) # Màu hồng cho nút Exit
OVERLAY_COLOR = (0, 0, 0, 180)     # Màu overlay cho popup

# Đường dẫn tài nguyên
ASSETS_PATH = r"C:\Users\ACER\Desktop\TTNT\Do_An_AI\assets"

class AssetManager:
    """Quản lý tất cả tài nguyên game"""
    @staticmethod
    def load_image(name: str, scale: float = 1.0) -> pygame.Surface:
        """Tải hình ảnh từ thư mục assets"""
        try:
            full_path = os.path.join(ASSETS_PATH, name)
            print(f"Loading image from: {full_path}")
            image = pygame.image.load(full_path).convert_alpha()
            if scale != 1.0:
                new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, new_size)
            return image
        except Exception as e:
            print(f"Error loading image {name}: {e}")
            # Fallback nếu không tải được ảnh
            surface = pygame.Surface((CELL_SIZE-10, CELL_SIZE-10), pygame.SRCALPHA)
            pygame.draw.rect(surface, (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)), 
                            (0, 0, CELL_SIZE-10, CELL_SIZE-10), border_radius=10)
            return surface

    @staticmethod
    def load_sound(name: str) -> Optional[pygame.mixer.Sound]:
        """Tải âm thanh từ thư mục assets"""
        try:
            full_path = os.path.join(ASSETS_PATH, name)
            print(f"Loading sound from: {full_path}")
            return pygame.mixer.Sound(full_path)
        except Exception as e:
            print(f"Error loading sound {name}: {e}")
            return None

class Button:
    """Lớp quản lý nút bấm trong game"""
    def __init__(self, x: int, y: int, text: str, width: int = 80, height: int = 80, 
                 color=BUTTON_COLOR, hover_color=None, text_color=WHITE, font_size=24, 
                 image=None, hover_image=None, border_radius=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.color = color
        self.hover_color = hover_color or (
            max(0, color[0]-30), 
            max(0, color[1]-30), 
            max(0, color[2]-30)
        )
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.image = image
        self.hover_image = hover_image
        self.border_radius = border_radius
        self.shadow_offset = 3  # Độ lệch của bóng đổ giảm xuống
        
    def draw(self, surface: pygame.Surface) -> None:
        """Vẽ nút lên surface với hiệu ứng đẹp hơn"""
        # Vẽ bóng đổ
        shadow_rect = pygame.Rect(
            self.rect.x + self.shadow_offset,
            self.rect.y + self.shadow_offset,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=self.border_radius)
        
        if self.image and self.hover_image:
            img = self.hover_image if self.is_hovered else self.image
            surface.blit(img, self.rect)
        else:
            color = self.hover_color if self.is_hovered else self.color
            
            # Vẽ nút với hiệu ứng gradient
            for i in range(self.rect.height):
                gradient_color = (
                    max(0, color[0] - i//2),
                    max(0, color[1] - i//2),
                    max(0, color[2] - i//2)
                )
                pygame.draw.rect(surface, gradient_color, 
                                (self.rect.x, self.rect.y + i, self.rect.width, 1))
            
            # Vẽ viền
            pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=self.border_radius)
        
        # Vẽ chữ với hiệu ứng bóng
        text_shadow = self.font.render(self.text, True, (0, 0, 0))
        text_surf = self.font.render(self.text, True, self.text_color)
        
        text_rect = text_surf.get_rect(center=self.rect.center)
        shadow_rect = text_shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
        
        surface.blit(text_shadow, shadow_rect)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos: Tuple[int, int]) -> bool:
        """Kiểm tra chuột có hover vào nút không"""
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos: Tuple[int, int], event: pygame.event.Event) -> bool:
        """Kiểm tra nút có được click không"""
        return event.type == MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(pos)

class Animation:
    """Lớp quản lý hiệu ứng hoạt hình trong game"""
    def __init__(self, candy_images):
        self.animations: List[Dict] = []
        self.candy_images = candy_images
        
    def add_animation(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                     candy_type: int, is_swapping: bool = False) -> None:
        """Thêm hiệu ứng mới"""
        self.animations.append({
            'start_pos': start_pos,
            'end_pos': end_pos,
            'current_pos': list(start_pos),
            'candy_type': candy_type,
            'progress': 0,
            'is_swapping': is_swapping,
            'scale': 1.0,  # Thêm hiệu ứng co giãn
            'rotation': 0  # Thêm hiệu ứng xoay
        })
        
    def update(self) -> None:
        """Cập nhật trạng thái hiệu ứng"""
        for anim in self.animations[:]:
            anim['progress'] += ANIMATION_SPEED
            if anim['progress'] >= 100:
                anim['current_pos'] = anim['end_pos']
                self.animations.remove(anim)
            else:
                # Cập nhật vị trí
                dx = anim['end_pos'][0] - anim['start_pos'][0]
                dy = anim['end_pos'][1] - anim['start_pos'][1]
                progress = anim['progress'] / 100
                
                # Thêm hiệu ứng easing
                if anim['is_swapping']:
                    # Sử dụng hàm sine để tạo hiệu ứng mượt mà
                    ease = math.sin(progress * math.pi / 2)
                    anim['current_pos'][0] = anim['start_pos'][0] + dx * ease
                    anim['current_pos'][1] = anim['start_pos'][1] + dy * ease
                    
                    # Hiệu ứng co giãn và xoay
                    anim['scale'] = 1.0 + 0.2 * math.sin(progress * math.pi)
                    anim['rotation'] = 30 * math.sin(progress * math.pi)
                else:
                    # Hiệu ứng rơi với trọng lực
                    anim['current_pos'][0] = anim['start_pos'][0] + dx * progress
                    anim['current_pos'][1] = anim['start_pos'][1] + dy * (progress * progress)
                
    def draw(self, surface: pygame.Surface) -> None:
        """Vẽ hiệu ứng lên surface"""
        for anim in self.animations:
            x, y = anim['current_pos']
            candy_type = anim['candy_type']
            
            if 0 <= candy_type < len(self.candy_images):
                # Lấy hình ảnh kẹo
                candy_img = self.candy_images[candy_type]
                
                # Áp dụng hiệu ứng co giãn và xoay
                if anim['is_swapping']:
                    # Tạo bản sao để không ảnh hưởng đến hình ảnh gốc
                    scaled_img = pygame.transform.scale(
                        candy_img, 
                        (int(candy_img.get_width() * anim['scale']), 
                         int(candy_img.get_height() * anim['scale']))
                    )
                    
                    # Xoay hình ảnh
                    rotated_img = pygame.transform.rotate(scaled_img, anim['rotation'])
                    
                    # Tính toán vị trí để giữ kẹo ở giữa
                    candy_rect = rotated_img.get_rect(
                        center=(MARGIN + x * CELL_SIZE + CELL_SIZE//2, 
                               MARGIN + y * CELL_SIZE + CELL_SIZE//2 + 100)
                    )
                    surface.blit(rotated_img, candy_rect)
                else:
                    # Vẽ bình thường cho hiệu ứng rơi
                    candy_rect = candy_img.get_rect(
                        center=(MARGIN + x * CELL_SIZE + CELL_SIZE//2, 
                               MARGIN + y * CELL_SIZE + CELL_SIZE//2 + 100)
                    )
                    surface.blit(candy_img, candy_rect)
            
    def is_animating(self) -> bool:
        """Kiểm tra có hiệu ứng đang chạy không"""
        return len(self.animations) > 0

class CandyCrushGame:
    """Lớp chính quản lý game"""
    def __init__(self):
        # Khởi tạo pygame
        pygame.init()
        pygame.mixer.init()
        
        # Tạo cửa sổ game
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Candy Crush Suga')
        self.clock = pygame.time.Clock()
        
        # Tải tài nguyên
        self.load_assets()
        
        # Khởi tạo các thuộc tính game
        self.board = []
        self.selected = None
        self.score = 0
        self.moves = 15
        self.level = 1
        self.target_score = 1000
        self.game_state = "MENU"  # MENU, PLAYING, GAME_OVER, LEVEL_COMPLETE
        self.animation = Animation(self.candy_images)
        
        # Font chữ
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 24)
        
        # Các nút - Điều chỉnh kích thước và vị trí
        button_size = CELL_SIZE  # Kích thước nút bằng kích thước ô
        
        # Nút menu chính
        self.start_button = Button(
            WINDOW_WIDTH//2 - button_size//2, 
            450, 
            "Play", 
            width=button_size, 
            height=button_size,
            color=BUTTON_COLOR,
            font_size=28
        )
        
        self.exit_button = Button(
            WINDOW_WIDTH//2 - button_size//2, 
            550, 
            "Exit", 
            width=button_size, 
            height=button_size,
            color=BUTTON_EXIT_COLOR,
            font_size=28
        )
        
        # Nút trong game
        self.menu_button = Button(
            WINDOW_WIDTH - button_size - 10, 
            WINDOW_HEIGHT - button_size - 10, 
            "Menu", 
            width=button_size, 
            height=button_size,
            color=BUTTON_EXIT_COLOR,
            font_size=24
        )
        
        # Nút kết thúc game
        self.restart_button = Button(
            WINDOW_WIDTH//2 - button_size - 10, 
            WINDOW_HEIGHT//2 + 100, 
            "Retry",
            width=button_size, 
            height=button_size,
            color=BUTTON_COLOR,
            font_size=24
        )
        
        self.back_to_menu_button = Button(
            WINDOW_WIDTH//2 + 10, 
            WINDOW_HEIGHT//2 + 100, 
            "Menu",
            width=button_size, 
            height=button_size,
            color=BUTTON_EXIT_COLOR,
            font_size=24
        )
        
        # Nút hoàn thành màn
        self.next_level_button = Button(
            WINDOW_WIDTH//2 - button_size - 10, 
            WINDOW_HEIGHT//2 + 100, 
            "Next",
            width=button_size, 
            height=button_size,
            color=BUTTON_COLOR,
            font_size=24
        )
        
        # Hiệu ứng
        self.particles = []
        self.stars = self.generate_stars(100)
        
        # Khởi tạo bảng
        self.initialize_board()
    
    def load_assets(self):
        """Tải tất cả tài nguyên game"""
        try:
            # Kiểm tra thư mục assets tồn tại
            if not os.path.exists(ASSETS_PATH):
                print(f"Warning: Assets directory {ASSETS_PATH} does not exist!")
                os.makedirs(ASSETS_PATH, exist_ok=True)
            
            # Hình ảnh
            self.background_img = pygame.transform.scale(
                AssetManager.load_image('background.jpg'), 
                (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
            
            # Tải logo
            self.logo_img = AssetManager.load_image('candy_crush_logo.png', 0.7)
            
            # Tải hình ảnh kẹo
            self.candy_images = []
            for candy_type in ['candy_red.png', 'candy_blue.png', 'candy_green.png', 
                           'candy_yellow.png', 'candy_orange.png', 'candy_purple.png']:
                candy_img = AssetManager.load_image(candy_type, 0.4)
                self.candy_images.append(candy_img)
            
            # Tải hình ảnh kẹo tùy chỉnh
            try:
                # Tải kẹo bom màu
                color_bomb_img = AssetManager.load_image('colour_bomb.png', 0.4)
                if color_bomb_img:
                    self.special_candy_images['color_bomb'] = color_bomb_img
                    print("Loaded color bomb image successfully")
                
                # Tải kẹo đỏ
                red_candy_img = AssetManager.load_image('red_candy.png', 0.4)
                if red_candy_img and len(self.candy_images) > 0:
                    # Thay thế kẹo đỏ đầu tiên
                    self.candy_images[0] = red_candy_img
                    print("Loaded red candy image successfully")
                
                # Tải kẹo sọc
                striped_candy_img = AssetManager.load_image('striped_candy.png', 0.4)
                if striped_candy_img and len(self.special_candy_images['striped_horizontal']) > 0:
                    # Thay thế kẹo sọc ngang đầu tiên
                    self.special_candy_images['striped_horizontal'][0] = striped_candy_img
                    print("Loaded striped candy image successfully")
            except Exception as e:
                print(f"Error loading custom candy images: {e}")
            
            # Tải hình ảnh kẹo đặc biệt
            self.special_candy_images = {
                'striped_horizontal': [],
                'striped_vertical': [],
                'wrapped': [],
                'color_bomb': None
            }
            
            # Tạo kẹo sọc ngang và dọc cho mỗi màu
            for i, candy_img in enumerate(self.candy_images):
                # Kẹo sọc ngang
                striped_h = candy_img.copy()
                for y in range(0, striped_h.get_height(), 8):
                    pygame.draw.line(striped_h, WHITE, (0, y), (striped_h.get_width(), y), 3)
                self.special_candy_images['striped_horizontal'].append(striped_h)
                
                # Kẹo sọc dọc
                striped_v = candy_img.copy()
                for x in range(0, striped_v.get_width(), 8):
                    pygame.draw.line(striped_v, WHITE, (x, 0), (x, striped_v.get_height()), 3)
                self.special_candy_images['striped_vertical'].append(striped_v)
                
                # Kẹo gói
                wrapped = candy_img.copy()
                pygame.draw.rect(wrapped, WHITE, (wrapped.get_width()//4, wrapped.get_height()//4, 
                                                wrapped.get_width()//2, wrapped.get_height()//2), 3)
                self.special_candy_images['wrapped'].append(wrapped)
            
            # Tạo kẹo bom màu
            self.special_candy_images['color_bomb'] = self.create_color_bomb_image()
            
            # Tải hình ảnh nút
            self.button_img = AssetManager.load_image('button.png', 0.2)
            self.button_hover_img = AssetManager.load_image('button_hover.png', 0.2)
            
            # Tải hình ảnh khung
            self.frame_img = AssetManager.load_image('frame.png', 0.3)
            
            # Âm thanh
            self.swap_sound = AssetManager.load_sound('swap.wav')
            self.match_sound = AssetManager.load_sound('match.wav')
            self.level_up_sound = AssetManager.load_sound('level_up.wav')
            self.game_over_sound = AssetManager.load_sound('game_over.wav')
            
            # Nhạc nền
            music_path = os.path.join(ASSETS_PATH, 'background_music.mp3')
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)
                print("Nhạc đã được tải!")
            else:
                print(f"Lỗi: Không tìm thấy file {music_path}")
        
        except Exception as e:
            print(f"Lỗi tải tài nguyên: {e}")
            self.background_img = None
            self.logo_img = None
            self.candy_images = []
            self.button_img = None
            self.button_hover_img = None
            self.frame_img = None
            self.swap_sound = None
            self.match_sound = None
            self.level_up_sound = None
            self.game_over_sound = None
    
    def create_color_bomb_image(self):
        """Tạo hình ảnh kẹo bom màu"""
        # Tạo bề mặt cho kẹo bom màu
        color_bomb = pygame.Surface((CELL_SIZE-10, CELL_SIZE-10), pygame.SRCALPHA)
        
        # Vẽ nền đen cho kẹo
        pygame.draw.circle(color_bomb, (30, 30, 30), (CELL_SIZE//2-5, CELL_SIZE//2-5), CELL_SIZE//2-10)
        
        # Thêm các chấm màu sắc
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), 
                  (255, 0, 255), (0, 255, 255), (255, 165, 0), (255, 192, 203)]
        
        for _ in range(15):  # Thêm 15 chấm màu
            color = random.choice(colors)
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(5, CELL_SIZE//2-15)
            x = CELL_SIZE//2-5 + int(distance * math.cos(angle))
            y = CELL_SIZE//2-5 + int(distance * math.sin(angle))
            radius = random.randint(2, 5)
            pygame.draw.circle(color_bomb, color, (x, y), radius)
        
        return color_bomb
    
    def generate_stars(self, count):
        """Tạo các ngôi sao cho background"""
        stars = []
        for _ in range(count):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            stars.append({
                'pos': (x, y),
                'size': size,
                'color': (brightness, brightness, brightness),
                'speed': random.uniform(0.1, 0.3)
            })
        return stars
    
    def update_stars(self):
        """Cập nhật vị trí các ngôi sao"""
        for star in self.stars:
            star['pos'] = (
                (star['pos'][0] + star['speed']) % WINDOW_WIDTH,
                star['pos'][1]
            )
    
    def draw_stars(self):
        """Vẽ các ngôi sao lên background"""
        for star in self.stars:
            pygame.draw.circle(
                self.window, 
                star['color'], 
                (int(star['pos'][0]), int(star['pos'][1])), 
                star['size']
            )
    
    def add_particle(self, pos, color):
        """Thêm hiệu ứng particle"""
        for _ in range(10):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(1, 5)
            size = random.randint(2, 6)
            lifetime = random.randint(20, 40)
            self.particles.append({
                'pos': list(pos),
                'vel': [speed * math.cos(angle), speed * math.sin(angle)],
                'size': size,
                'color': color,
                'lifetime': lifetime,
                'max_lifetime': lifetime
            })
    
    def update_particles(self):
        """Cập nhật các particle"""
        for particle in self.particles[:]:
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                continue
            
            # Cập nhật vị trí
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            
            # Giảm vận tốc
            particle['vel'][0] *= 0.95
            particle['vel'][1] *= 0.95
            
            # Thêm trọng lực
            particle['vel'][1] += 0.1
    
    def draw_particles(self):
        """Vẽ các particle"""
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            color = (*particle['color'], alpha)
            
            surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (particle['size'], particle['size']), particle['size'])
            
            self.window.blit(surf, (particle['pos'][0] - particle['size'], particle['pos'][1] - particle['size']))
    
    def initialize_board(self) -> None:
        """Khởi tạo bảng game ngẫu nhiên"""
        self.board = []
        # Check if candy_images is properly loaded
        if not self.candy_images or len(self.candy_images) == 0:
            print("Warning: No candy images loaded, using 6 placeholder types")
            num_candy_types = 6
        else:
            num_candy_types = len(self.candy_images)
        
        # Khởi tạo bảng với các kẹo thường
        for _ in range(BOARD_SIZE):
            row = []
            for _ in range(BOARD_SIZE):
                # Mỗi kẹo là một từ điển chứa loại và thuộc tính đặc biệt
                row.append({
                    'type': random.randint(0, num_candy_types-1),
                    'special': None  # None, 'striped_horizontal', 'striped_vertical', 'wrapped', 'color_bomb'
                })
            self.board.append(row)
        
        # Đảm bảo không có nước đi hợp lệ ngay từ đầu
        while self.find_matches(False):
            self.remove_matches()
            self.fill_board()
            
        # Đảm bảo không có ô trống sau khi khởi tạo
        self.ensure_no_empty_cells()
    
    def ensure_no_empty_cells(self) -> None:
        """Đảm bảo không có ô trống trên bảng"""
        if not self.candy_images or len(self.candy_images) == 0:
            num_candy_types = 6
        else:
            num_candy_types = len(self.candy_images)
            
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.board[y][x]['type'] == -1:
                    # Nếu phát hiện ô trống, điền kẹo mới
                    self.board[y][x] = {
                        'type': random.randint(0, num_candy_types-1),
                        'special': None
                    }
    
    def draw(self) -> None:
        """Vẽ toàn bộ game"""
        # Vẽ nền
        if self.background_img:
            self.window.blit(self.background_img, (0, 0))
        else:
            self.window.fill(BACKGROUND_COLOR)
            self.draw_stars()
        
        # Vẽ theo trạng thái game
        {
            "MENU": self.draw_menu,
            "PLAYING": self.draw_game,
            "GAME_OVER": self.draw_game_over,
            "LEVEL_COMPLETE": self.draw_level_complete
        }.get(self.game_state, self.draw_menu)()
        
        # Vẽ particles
        self.draw_particles()
    
    def draw_menu(self) -> None:
        """Vẽ màn hình menu"""
        # Vẽ khung trang trí
        if self.frame_img:
            frame_rect = self.frame_img.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.window.blit(self.frame_img, frame_rect)
        
        # Tiêu đề
        if self.logo_img:
            logo_rect = self.logo_img.get_rect(center=(WINDOW_WIDTH//2, 200))
            self.window.blit(self.logo_img, logo_rect)
        else:
            # Vẽ tiêu đề với hiệu ứng bóng
            title_shadow = self.font_large.render("Candy Crush Suga", True, BLACK)
            title = self.font_large.render("Candy Crush Suga", True, TEXT_COLOR)
            
            title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 200))
            shadow_rect = title_shadow.get_rect(center=(title_rect.centerx + 3, title_rect.centery + 3))
            
            self.window.blit(title_shadow, shadow_rect)
            self.window.blit(title, title_rect)
        
        # Các nút
        self.start_button.draw(self.window)
        self.exit_button.draw(self.window)
        
        # Hướng dẫn
        instructions = [
            "Cach choi: ",
            "Click vao 1 vien keo de chon",
            "Click vào vien keo lien ke de hoan doi",
            "Ghep 3 hoac nhieu keo cung mau de no",
            "Dat du diem muc tieu de qua man"
        ]
        
        # Vẽ hộp hướng dẫn
        instruction_box = pygame.Rect(WINDOW_WIDTH//2 - 250, 300, 500, 130)
        pygame.draw.rect(self.window, (255, 255, 255, 180), instruction_box, border_radius=15)
        pygame.draw.rect(self.window, TEXT_COLOR, instruction_box, 2, border_radius=15)
        
        for i, line in enumerate(instructions):
            text_shadow = self.font_tiny.render(line, True, (0, 0, 0))
            text = self.font_tiny.render(line, True, TEXT_COLOR)
            
            text_rect = text.get_rect(midleft=(WINDOW_WIDTH//2 - 230, 320 + i * 24))
            shadow_rect = text_shadow.get_rect(midleft=(text_rect.left + 2, text_rect.centery + 2))
            
            self.window.blit(text_shadow, shadow_rect)
            self.window.blit(text, text_rect)
    
    def draw_game(self) -> None:
        """Vẽ màn hình chơi game"""
        # Vẽ khung thông tin
        info_box = pygame.Rect(20, 20, WINDOW_WIDTH - 40, 60)
        pygame.draw.rect(self.window, (255, 255, 255, 180), info_box, border_radius=15)
        pygame.draw.rect(self.window, TEXT_COLOR, info_box, 2, border_radius=15)
        
        # Thông tin game
        score_text = self.font_medium.render(f"Diem: {self.score}/{self.target_score}", True, TEXT_COLOR)
        moves_text = self.font_medium.render(f"Luot: {self.moves}", True, TEXT_COLOR)
        level_text = self.font_medium.render(f"Man: {self.level}", True, TEXT_COLOR)
        
        self.window.blit(score_text, (40, 30))
        self.window.blit(moves_text, (WINDOW_WIDTH - 180, 30))
        self.window.blit(level_text, (WINDOW_WIDTH//2 - 50, 30))
        
        # Vẽ khung bảng game
        board_box = pygame.Rect(
            MARGIN - 10, 
            MARGIN + 80, 
            BOARD_SIZE * CELL_SIZE + 20, 
            BOARD_SIZE * CELL_SIZE + 20
        )
        pygame.draw.rect(self.window, (255, 255, 255, 180), board_box, border_radius=15)
        pygame.draw.rect(self.window, TEXT_COLOR, board_box, 3, border_radius=15)
        
        # Bảng game
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                rect = pygame.Rect(
                    MARGIN + x * CELL_SIZE,
                    MARGIN + y * CELL_SIZE + 100,
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                # Vẽ ô lưới với hiệu ứng gradient
                pygame.draw.rect(self.window, GRID_COLOR, rect, border_radius=10)
                
                # Vẽ viền ô
                pygame.draw.rect(self.window, WHITE, rect, 2, border_radius=10)
                
                # Vẽ kẹo
                if not self.animation.is_animating() or not self.is_candy_animating(x, y):
                    candy = self.board[y][x]
                    candy_type = candy['type']
                    special = candy['special']
                    
                    if candy_type != -1:  # -1 là ô trống
                        # Vẽ kẹo đặc biệt nếu có
                        if special == 'striped_horizontal' and 0 <= candy_type < len(self.special_candy_images['striped_horizontal']):
                            candy_img = self.special_candy_images['striped_horizontal'][candy_type]
                        elif special == 'striped_vertical' and 0 <= candy_type < len(self.special_candy_images['striped_vertical']):
                            candy_img = self.special_candy_images['striped_vertical'][candy_type]
                        elif special == 'wrapped' and 0 <= candy_type < len(self.special_candy_images['wrapped']):
                            candy_img = self.special_candy_images['wrapped'][candy_type]
                        elif special == 'color_bomb':
                            candy_img = self.special_candy_images['color_bomb']
                        elif 0 <= candy_type < len(self.candy_images):
                            candy_img = self.candy_images[candy_type]
                        else:
                            continue
                            
                        candy_rect = candy_img.get_rect(center=rect.center)
                        self.window.blit(candy_img, candy_rect)
                        
                        # Đánh dấu ô được chọn với hiệu ứng sáng
                        if self.selected == (x, y):
                            # Vẽ viền sáng
                            glow_size = 4
                            glow_rect = pygame.Rect(
                                rect.x - glow_size, 
                                rect.y - glow_size,
                                rect.width + glow_size * 2,
                                rect.height + glow_size * 2
                            )
                            pygame.draw.rect(self.window, (255, 255, 0), glow_rect, glow_size, border_radius=15)
        
        # Hiệu ứng
        self.animation.draw(self.window)
        
        # Nút về menu
        self.menu_button.draw(self.window)
    
    def draw_game_over(self) -> None:
        """Vẽ màn hình kết thúc game"""
        # Lớp phủ mờ
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        self.window.blit(overlay, (0, 0))
        
        # Vẽ khung thông báo
        popup_rect = pygame.Rect(WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(self.window, WHITE, popup_rect, border_radius=20)
        pygame.draw.rect(self.window, TEXT_COLOR, popup_rect, 3, border_radius=20)
        
        # Thông báo
        game_over = self.font_large.render("Game Over!", True, TEXT_COLOR)
        score_text = self.font_medium.render(f"Điểm: {self.score}", True, TEXT_COLOR)
        target_text = self.font_medium.render(f"Mục tiêu: {self.target_score}", True, TEXT_COLOR)
        
        self.window.blit(game_over, game_over.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 80)))
        self.window.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20)))
        self.window.blit(target_text, target_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20)))
        
        # Nút
        self.restart_button.draw(self.window)
        self.back_to_menu_button.draw(self.window)
    
    def draw_level_complete(self) -> None:
        """Vẽ màn hình hoàn thành màn chơi"""
        # Lớp phủ mờ
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        self.window.blit(overlay, (0, 0))
        
        # Vẽ khung thông báo
        popup_rect = pygame.Rect(WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(self.window, WHITE, popup_rect, border_radius=20)
        pygame.draw.rect(self.window, TEXT_COLOR, popup_rect, 3, border_radius=20)
        
        # Thông báo
        complete = self.font_large.render(f"Màn {self.level}", True, TEXT_COLOR)
        complete2 = self.font_medium.render("Hoàn Thành!", True, TEXT_COLOR)
        score_text = self.font_medium.render(f"Điểm: {self.score}", True, TEXT_COLOR)
        bonus_text = self.font_medium.render(f"Thưởng: +{self.moves * 10}", True, TEXT_COLOR)
        
        self.window.blit(complete, complete.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 80)))
        self.window.blit(complete2, complete2.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30)))
        self.window.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 10)))
        self.window.blit(bonus_text, bonus_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50)))
        
        # Nút
        self.next_level_button.draw(self.window)
        self.back_to_menu_button.draw(self.window)
        
        # Hiệu ứng pháo hoa
        if random.random() < 0.05:  # 5% cơ hội mỗi frame
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT//2)
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            self.add_particle((x, y), color)
    
    def is_candy_animating(self, x: int, y: int) -> bool:
        """Kiểm tra kẹo có đang trong hiệu ứng không"""
        return any(anim['end_pos'] == (x, y) or anim['start_pos'] == (x, y) 
                  for anim in self.animation.animations)
    
    def handle_events(self) -> None:
        """Xử lý sự kiện game"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if self.game_state == "MENU":
                self.start_button.check_hover(mouse_pos)
                self.exit_button.check_hover(mouse_pos)
                
                if self.start_button.is_clicked(mouse_pos, event):
                    self.game_state = "PLAYING"
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play(-1)
                
                if self.exit_button.is_clicked(mouse_pos, event):
                    pygame.quit()
                    sys.exit()
            
            elif self.game_state == "PLAYING":
                self.menu_button.check_hover(mouse_pos)
                
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu_button.is_clicked(mouse_pos, event):
                        self.game_state = "MENU"
                    else:
                        self.handle_click(mouse_pos)
            
            elif self.game_state == "GAME_OVER":
                self.restart_button.check_hover(mouse_pos)
                self.back_to_menu_button.check_hover(mouse_pos)
                
                if self.restart_button.is_clicked(mouse_pos, event):
                    self.reset_game()
                    self.game_state = "PLAYING"
                
                if self.back_to_menu_button.is_clicked(mouse_pos, event):
                    self.game_state = "MENU"
            
            elif self.game_state == "LEVEL_COMPLETE":
                self.next_level_button.check_hover(mouse_pos)
                self.back_to_menu_button.check_hover(mouse_pos)
                
                if self.next_level_button.is_clicked(mouse_pos, event):
                    self.level_up()
                
                if self.back_to_menu_button.is_clicked(mouse_pos, event):
                    self.game_state = "MENU"
    
    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Xử lý click chuột trên bảng game"""
        if self.animation.is_animating():
            return
            
        # Kiểm tra click trong vùng bảng
        x, y = pos[0], pos[1]
        if (MARGIN <= x < MARGIN + BOARD_SIZE * CELL_SIZE and 
            MARGIN + 100 <= y < MARGIN + 100 + BOARD_SIZE * CELL_SIZE):
            grid_x = (x - MARGIN) // CELL_SIZE
            grid_y = (y - MARGIN - 100) // CELL_SIZE
            
            if self.selected is None:
                self.selected = (grid_x, grid_y)
                # Thêm hiệu ứng âm thanh khi chọn
                if self.swap_sound:
                    self.swap_sound.play()
            else:
                # Kiểm tra ô được chọn có liền kề không
                x1, y1 = self.selected
                if ((abs(x1 - grid_x) == 1 and y1 == grid_y) or 
                    (abs(y1 - grid_y) == 1 and x1 == grid_x)):
                    self.swap_and_check((x1, y1), (grid_x, grid_y))
                
                self.selected = None
    
    def swap_and_check(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> None:
        """Hoán đổi và kiểm tra nước đi hợp lệ"""
        self.swap_candies_with_animation(pos1, pos2)
        self.moves -= 1
        
        # Kiểm tra nếu không có nước đi hợp lệ thì hoàn tác
        if not self.find_matches(False):
            pygame.time.set_timer(USEREVENT + 1, 300, True)
        else:
            pygame.time.set_timer(USEREVENT + 2, 300, True)
    
    def swap_candies_with_animation(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> None:
        """Hoán đổi kẹo với hiệu ứng"""
        x1, y1 = pos1
        x2, y2 = pos2
        
        # Thêm hiệu ứng
        self.animation.add_animation(pos1, pos2, self.board[y1][x1]['type'], True)
        self.animation.add_animation(pos2, pos1, self.board[y2][x2]['type'], True)
        
        # Thực sự hoán đổi trên bảng
        self.board[y1][x1], self.board[y2][x2] = self.board[y2][x2], self.board[y1][x1]
        
        # Phát âm thanh
        if self.swap_sound:
            self.swap_sound.play()
    
    def find_matches(self, remove: bool = False) -> bool:
        """Tìm và xử lý các kẹo khớp nhau"""
        matches_found = False
        matches_info = []  # Lưu thông tin về các kẹo khớp nhau
        
        # Tìm các kẹo khớp theo hàng
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE - 2):
                if (x + 2 < BOARD_SIZE and 
                    self.board[y][x]['type'] != -1 and
                    self.board[y][x]['type'] == self.board[y][x+1]['type'] == self.board[y][x+2]['type']):
                    
                    # Tìm độ dài của chuỗi khớp
                    match_length = 3
                    while x + match_length < BOARD_SIZE and self.board[y][x]['type'] == self.board[y][x+match_length]['type']:
                        match_length += 1
                    
                    # Lưu thông tin về chuỗi khớp
                    matches_info.append({
                        'type': 'horizontal',
                        'length': match_length,
                        'start': (x, y),
                        'candy_type': self.board[y][x]['type']
                    })
                    
                    # Đánh dấu các kẹo khớp
                    matches = [(x+i, y) for i in range(match_length)]
                    
                    if remove:
                        for mx, my in matches:
                            # Thêm hiệu ứng particle khi nổ kẹo
                            candy_center = (
                                MARGIN + mx * CELL_SIZE + CELL_SIZE//2,
                                MARGIN + my * CELL_SIZE + CELL_SIZE//2 + 100
                            )
                            candy_type = self.board[my][mx]['type']
                            if candy_type != -1:
                                # Lấy màu chủ đạo của viên kẹo
                                candy_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                                self.add_particle(candy_center, candy_color)
                            
                            # Xóa kẹo
                            self.board[my][mx] = {'type': -1, 'special': None}
                    
                    matches_found = True
                    x += match_length - 1  # Bỏ qua các kẹo đã kiểm tra
        
        # Tìm các kẹo khớp theo cột
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE - 2):
                if (y + 2 < BOARD_SIZE and 
                    self.board[y][x]['type'] != -1 and
                    self.board[y][x]['type'] == self.board[y+1][x]['type'] == self.board[y+2][x]['type']):
                    
                    # Tìm độ dài của chuỗi khớp
                    match_length = 3
                    while y + match_length < BOARD_SIZE and self.board[y][x]['type'] == self.board[y+match_length][x]['type']:
                        match_length += 1
                    
                    # Lưu thông tin về chuỗi khớp
                    matches_info.append({
                        'type': 'vertical',
                        'length': match_length,
                        'start': (x, y),
                        'candy_type': self.board[y][x]['type']
                    })
                    
                    # Đánh dấu các kẹo khớp
                    matches = [(x, y+i) for i in range(match_length)]
                    
                    if remove:
                        for mx, my in matches:
                            # Thêm hiệu ứng particle khi nổ kẹo
                            candy_center = (
                                MARGIN + mx * CELL_SIZE + CELL_SIZE//2,
                                MARGIN + my * CELL_SIZE + CELL_SIZE//2 + 100
                            )
                            candy_type = self.board[my][mx]['type']
                            if candy_type != -1:
                                # Lấy màu chủ đạo của viên kẹo
                                candy_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                                self.add_particle(candy_center, candy_color)
                            
                            # Xóa kẹo
                            self.board[my][mx] = {'type': -1, 'special': None}
                    
                    matches_found = True
                    y += match_length - 1  # Bỏ qua các kẹo đã kiểm tra
        
        # Tạo kẹo đặc biệt nếu có 4 kẹo trở lên khớp nhau
        if remove and matches_found:
            for match in matches_info:
                if match['length'] >= 4:
                    # Tạo kẹo đặc biệt
                    special_type = None
                    x, y = match['start']
                    
                    if match['length'] == 4:
                        # Kẹo sọc
                        if match['type'] == 'horizontal':
                            special_type = 'striped_vertical'  # Kẹo sọc dọc khi khớp ngang
                        else:
                            special_type = 'striped_horizontal'  # Kẹo sọc ngang khi khớp dọc
                    elif match['length'] >= 5:
                        # Kẹo bom màu
                        special_type = 'color_bomb'
                    
                    if special_type:
                        # Đặt kẹo đặc biệt vào vị trí đầu tiên của chuỗi khớp
                        self.board[y][x] = {
                            'type': match['candy_type'],
                            'special': special_type
                        }
        
        # Tính điểm
        self.score += len(matches_info) * 10
        
        if self.match_sound:
            self.match_sound.play()
    
        return matches_found
    
    def remove_matches(self) -> None:
        """Xóa các kẹo khớp nhau"""
        self.find_matches(True)
    
    def fill_board(self) -> None:
        """Điền kẹo mới vào bảng"""
        for x in range(BOARD_SIZE):
            empty_cells = []
            for y in range(BOARD_SIZE-1, -1, -1):
                if self.board[y][x]['type'] == -1:
                    empty_cells.append(y)
                elif empty_cells:
                    # Di chuyển kẹo xuống ô trống
                    lowest_empty = empty_cells.pop(0)
                    self.board[lowest_empty][x] = self.board[y][x]
                    self.board[y][x] = {'type': -1, 'special': None}
                    empty_cells.append(y)
                    
                    # Thêm hiệu ứng rơi
                    self.animation.add_animation((x, y), (x, lowest_empty), self.board[lowest_empty][x]['type'])
            
            # Điền kẹo mới
            for y in empty_cells:
                self.board[y][x] = {
                    'type': random.randint(0, len(self.candy_images)-1),
                    'special': None
                }
                self.animation.add_animation((x, y - len(empty_cells)), (x, y), self.board[y][x]['type'])
        
        # Kiểm tra lại một lần nữa để đảm bảo không có ô trống
        self.ensure_no_empty_cells()
    
    def process_matches(self) -> None:
        """Xử lý tất cả các kẹo khớp"""
        while True:
            self.remove_matches()
            if not self.find_matches(False):
                break
            self.fill_board()
        
        # Đảm bảo không có ô trống sau khi xử lý
        self.ensure_no_empty_cells()
        
        # Kiểm tra điều kiện thắng/thua
        if self.score >= self.target_score:
            self.game_state = "LEVEL_COMPLETE"
            if self.level_up_sound:
                self.level_up_sound.play()
        elif self.moves <= 0:
            self.game_state = "GAME_OVER"
            if self.game_over_sound:
                self.game_over_sound.play()
    
    def level_up(self) -> None:
        """Nâng cấp level"""
        # Thêm điểm thưởng cho số lượt còn lại
        self.score += self.moves * 10
        
        self.level += 1
        self.target_score = 1000 * self.level
        self.moves = 15 + self.level * 2
        self.initialize_board()
        self.game_state = "PLAYING"
    
    def reset_game(self) -> None:
        """Reset game về trạng thái ban đầu"""
        self.score = 0
        self.moves = 15
        self.level = 1
        self.target_score = 1000
        self.initialize_board()

    def activate_special_candy(self, x, y):
        """Kích hoạt hiệu ứng của kẹo đặc biệt"""
        candy = self.board[y][x]
        special_type = candy['special']
        candy_type = candy['type']
        
        if special_type == 'striped_horizontal':
            # Xóa toàn bộ hàng
            for col in range(BOARD_SIZE):
                if self.board[y][col]['type'] != -1:
                    # Thêm hiệu ứng particle
                    candy_center = (
                        MARGIN + col * CELL_SIZE + CELL_SIZE//2,
                        MARGIN + y * CELL_SIZE + CELL_SIZE//2 + 100
                    )
                    self.add_particle(candy_center, (255, 255, 255))
                    self.board[y][col] = {'type': -1, 'special': None}
            
            self.score += BOARD_SIZE * 10
            
        elif special_type == 'striped_vertical':
            # Xóa toàn bộ cột
            for row in range(BOARD_SIZE):
                if self.board[row][x]['type'] != -1:
                    # Thêm hiệu ứng particle
                    candy_center = (
                        MARGIN + x * CELL_SIZE + CELL_SIZE//2,
                        MARGIN + row * CELL_SIZE + CELL_SIZE//2 + 100
                    )
                    self.add_particle(candy_center, (255, 255, 255))
                    self.board[row][x] = {'type': -1, 'special': None}
            
            self.score += BOARD_SIZE * 10
            
        elif special_type == 'wrapped':
            # Xóa kẹo trong vùng 3x3
            for row in range(max(0, y-1), min(BOARD_SIZE, y+2)):
                for col in range(max(0, x-1), min(BOARD_SIZE, x+2)):
                    if self.board[row][col]['type'] != -1:
                        # Thêm hiệu ứng particle
                        candy_center = (
                            MARGIN + col * CELL_SIZE + CELL_SIZE//2,
                            MARGIN + row * CELL_SIZE + CELL_SIZE//2 + 100
                        )
                        self.add_particle(candy_center, (255, 255, 255))
                        self.board[row][col] = {'type': -1, 'special': None}
            
            self.score += 9 * 10  # 3x3 = 9 kẹo
            
        elif special_type == 'color_bomb':
            # Xóa tất cả kẹo cùng màu với kẹo được chọn
            target_type = candy_type
            count = 0
            
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    if self.board[row][col]['type'] == target_type and self.board[row][col]['type'] != -1:
                        # Thêm hiệu ứng particle
                        candy_center = (
                            MARGIN + col * CELL_SIZE + CELL_SIZE//2,
                            MARGIN + row * CELL_SIZE + CELL_SIZE//2 + 100
                        )
                        self.add_particle(candy_center, (255, 255, 255))
                        self.board[row][col] = {'type': -1, 'special': None}
                        count += 1
            
            self.score += count * 20  # Điểm cao hơn cho kẹo bom màu
        
        # Phát âm thanh
        if self.match_sound:
            self.match_sound.play()

    def swap_and_check(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> None:
        """Hoán đổi và kiểm tra nước đi hợp lệ"""
        x1, y1 = pos1
        x2, y2 = pos2
        
        # Kiểm tra xem có kẹo đặc biệt không
        candy1 = self.board[y1][x1]
        candy2 = self.board[y2][x2]
        
        # Nếu một trong hai kẹo là kẹo đặc biệt
        if candy1['special'] or candy2['special']:
            self.swap_candies_with_animation(pos1, pos2)
            self.moves -= 1
            
            # Kích hoạt kẹo đặc biệt
            if candy1['special']:
                self.activate_special_candy(x2, y2)  # Vị trí mới sau khi hoán đổi
            
            if candy2['special']:
                self.activate_special_candy(x1, y1)  # Vị trí mới sau khi hoán đổi
        
            # Điền kẹo mới và kiểm tra các kết hợp tiếp theo
            self.fill_board()
            pygame.time.set_timer(USEREVENT + 2, 300, True)
            return
        
        # Xử lý bình thường nếu không có kẹo đặc biệt
        self.swap_candies_with_animation(pos1, pos2)
        self.moves -= 1
        
        # Kiểm tra nếu không có nước đi hợp lệ thì hoàn tác
        if not self.find_matches(False):
            pygame.time.set_timer(USEREVENT + 1, 300, True)
        else:
            pygame.time.set_timer(USEREVENT + 2, 300, True)

    def find_matches(self, remove: bool = False) -> bool:
        """Tìm và xử lý các kẹo khớp nhau"""
        matches_found = False
        matches_info = []  # Lưu thông tin về các kẹo khớp nhau
        
        # Tìm các kẹo khớp theo hàng
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE - 2):
                if (x + 2 < BOARD_SIZE and 
                    self.board[y][x]['type'] != -1 and
                    self.board[y][x]['type'] == self.board[y][x+1]['type'] == self.board[y][x+2]['type']):
                
                    # Tìm độ dài của chuỗi khớp
                    match_length = 3
                    while x + match_length < BOARD_SIZE and self.board[y][x]['type'] == self.board[y][x+match_length]['type']:
                        match_length += 1
                
                    # Lưu thông tin về chuỗi khớp
                    matches_info.append({
                        'type': 'horizontal',
                        'length': match_length,
                        'start': (x, y),
                        'candy_type': self.board[y][x]['type']
                    })
                
                    # Đánh dấu các kẹo khớp
                    matches = [(x+i, y) for i in range(match_length)]
                
                    if remove:
                        for mx, my in matches:
                            # Thêm hiệu ứng particle khi nổ kẹo
                            candy_center = (
                                MARGIN + mx * CELL_SIZE + CELL_SIZE//2,
                                MARGIN + my * CELL_SIZE + CELL_SIZE//2 + 100
                            )
                            candy_type = self.board[my][mx]['type']
                            if candy_type != -1:
                                # Lấy màu chủ đạo của viên kẹo
                                candy_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                                self.add_particle(candy_center, candy_color)
                        
                            # Xóa kẹo
                            self.board[my][mx] = {'type': -1, 'special': None}
                
                    matches_found = True
                    x += match_length - 1  # Bỏ qua các kẹo đã kiểm tra
    
        # Tìm các kẹo khớp theo cột
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE - 2):
                if (y + 2 < BOARD_SIZE and 
                    self.board[y][x]['type'] != -1 and
                    self.board[y][x]['type'] == self.board[y+1][x]['type'] == self.board[y+2][x]['type']):
                
                    # Tìm độ dài của chuỗi khớp
                    match_length = 3
                    while y + match_length < BOARD_SIZE and self.board[y][x]['type'] == self.board[y+match_length][x]['type']:
                        match_length += 1
                
                    # Lưu thông tin về chuỗi khớp
                    matches_info.append({
                        'type': 'vertical',
                        'length': match_length,
                        'start': (x, y),
                        'candy_type': self.board[y][x]['type']
                    })
                
                    # Đánh dấu các kẹo khớp
                    matches = [(x, y+i) for i in range(match_length)]
                
                    if remove:
                        for mx, my in matches:
                            # Thêm hiệu ứng particle khi nổ kẹo
                            candy_center = (
                                MARGIN + mx * CELL_SIZE + CELL_SIZE//2,
                                MARGIN + my * CELL_SIZE + CELL_SIZE//2 + 100
                            )
                            candy_type = self.board[my][mx]['type']
                            if candy_type != -1:
                                # Lấy màu chủ đạo của viên kẹo
                                candy_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                                self.add_particle(candy_center, candy_color)
                        
                            # Xóa kẹo
                            self.board[my][mx] = {'type': -1, 'special': None}
                
                    matches_found = True
                    y += match_length - 1  # Bỏ qua các kẹo đã kiểm tra
    
        # Tạo kẹo đặc biệt nếu có 4 kẹo trở lên khớp nhau
        if remove and matches_found:
            for match in matches_info:
                if match['length'] >= 4:
                    # Tạo kẹo đặc biệt
                    special_type = None
                    x, y = match['start']
                
                    if match['length'] == 4:
                        # Kẹo sọc
                        if match['type'] == 'horizontal':
                            special_type = 'striped_vertical'  # Kẹo sọc dọc khi khớp ngang
                        else:
                            special_type = 'striped_horizontal'  # Kẹo sọc ngang khi khớp dọc
                    elif match['length'] >= 5:
                        # Kẹo bom màu
                        special_type = 'color_bomb'
                
                    if special_type:
                        # Đặt kẹo đặc biệt vào vị trí đầu tiên của chuỗi khớp
                        self.board[y][x] = {
                            'type': match['candy_type'],
                            'special': special_type
                        }
        
        # Tính điểm
        self.score += len(matches_info) * 10
        
        if self.match_sound:
            self.match_sound.play()
    
        return matches_found

    
    def remove_matches(self) -> None:
        """Xóa các kẹo khớp nhau"""
        self.find_matches(True)
    
    def fill_board(self) -> None:
        """Điền kẹo mới vào bảng"""
        for x in range(BOARD_SIZE):
            empty_cells = []
            for y in range(BOARD_SIZE-1, -1, -1):
                if self.board[y][x]['type'] == -1:
                    empty_cells.append(y)
                elif empty_cells:
                    # Di chuyển kẹo xuống ô trống
                    lowest_empty = empty_cells.pop(0)
                    self.board[lowest_empty][x] = self.board[y][x]
                    self.board[y][x] = {'type': -1, 'special': None}
                    empty_cells.append(y)
                    
                    # Thêm hiệu ứng rơi
                    self.animation.add_animation((x, y), (x, lowest_empty), self.board[lowest_empty][x]['type'])
            
            # Điền kẹo mới
            for y in empty_cells:
                self.board[y][x] = {
                    'type': random.randint(0, len(self.candy_images)-1),
                    'special': None
                }
                self.animation.add_animation((x, y - len(empty_cells)), (x, y), self.board[y][x]['type'])
    
    def process_matches(self) -> None:
        """Xử lý tất cả các kẹo khớp"""
        while True:
            self.remove_matches()
            if not self.find_matches(False):
                break
            self.fill_board()
        
        # Đảm bảo không có ô trống sau khi xử lý
        self.ensure_no_empty_cells()
        
        # Kiểm tra điều kiện thắng/thua
        if self.score >= self.target_score:
            self.game_state = "LEVEL_COMPLETE"
            if self.level_up_sound:
                self.level_up_sound.play()
        elif self.moves <= 0:
            self.game_state = "GAME_OVER"
            if self.game_over_sound:
                self.game_over_sound.play()
    
    def level_up(self) -> None:
        """Nâng cấp level"""
        # Thêm điểm thưởng cho số lượt còn lại
        self.score += self.moves * 10
        
        self.level += 1
        self.target_score = 1000 * self.level
        self.moves = 15 + self.level * 2
        self.initialize_board()
        self.game_state = "PLAYING"
    
    def reset_game(self) -> None:
        """Reset game về trạng thái ban đầu"""
        self.score = 0
        self.moves = 15
        self.level = 1
        self.target_score = 1000
        self.initialize_board()
    
    def update(self) -> None:
        """Cập nhật trạng thái game"""
        # Cập nhật hiệu ứng background
        self.update_stars()
        self.update_particles()
        
        if self.game_state == "PLAYING":
            self.animation.update()
            
            # Kiểm tra sự kiện timer
            for event in pygame.event.get(USEREVENT):
                if event.type == USEREVENT + 1:  # Hoàn tác hoán đổi không hợp lệ
                    x1, y1 = self.selected if self.selected else (0, 0)
                    x2, y2 = (x1+1, y1) if self.selected else (0, 0)
                    self.swap_candies_with_animation((x1, y1), (x2, y2))
                    self.moves += 1  # Hoàn lại lượt
                
                elif event.type == USEREVENT + 2:  # Xử lý nổ kẹo sau hoán đổi
                    self.process_matches()

def main():
    """Hàm chính chạy game"""
    game = CandyCrushGame()
    pygame.mixer.music.play(-1)
    
    while True:
        game.handle_events()
        game.update()
        game.draw()
        pygame.display.update()
        game.clock.tick(FPS)

if __name__ == "__main__":
    main()

