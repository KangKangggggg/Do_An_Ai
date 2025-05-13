import pygame
import random
import os
from constants import *

# Sửa lỗi tải hình ảnh bằng cách thêm cơ chế dự phòng
def load_image(path):
    try:
        print(f"Đang thử tải ảnh từ: {path}")
        if os.path.exists(path):
            return pygame.image.load(path)
        elif path.endswith('.png'):
            # Thử không có đuôi .png
            no_ext_path = path[:-4]
            if os.path.exists(no_ext_path):
                return pygame.image.load(no_ext_path)
        else:
            # Thử thêm đuôi .png
            png_path = path + '.png'
            if os.path.exists(png_path):
                return pygame.image.load(png_path)
        
        # Nếu không tìm thấy, tạo hình ảnh giả
        print(f"Không tìm thấy file: {path}")
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(surface, (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)), 
                          (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2 - 5)
        pygame.draw.circle(surface, (255, 255, 255), (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2 - 5, 2)
        return surface
    except pygame.error as e:
        print(f"Không thể tải ảnh: {path}, lỗi: {e}")
        # Tạo hình ảnh giả
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(surface, (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)), 
                          (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2 - 5)
        pygame.draw.circle(surface, (255, 255, 255), (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2 - 5, 2)
        return surface

# Thư mục chứa ảnh - sử dụng đường dẫn tương đối
import os
# Sử dụng đường dẫn tương đối thay vì tuyệt đối
script_dir = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(script_dir, "assets")
print(f"Candy: Đường dẫn assets: {ASSETS_DIR}")
print(f"Candy: Thư mục assets tồn tại: {os.path.exists(ASSETS_DIR)}")

# Liệt kê các file trong thư mục assets
if os.path.exists(ASSETS_DIR):
    print("Candy: Các file trong thư mục assets:")
    for file in os.listdir(ASSETS_DIR):
        print(f"  - {file}")
else:
    print(f"CẢNH BÁO: Không tìm thấy thư mục assets tại {ASSETS_DIR}")
    # Tạo thư mục assets nếu chưa tồn tại
    try:
        os.makedirs(ASSETS_DIR, exist_ok=True)
        print(f"Đã tạo thư mục assets tại {ASSETS_DIR}")
    except Exception as e:
        print(f"Không thể tạo thư mục assets: {e}")

# Danh sách tên kẹo
candies = ["candy_red", "candy_blue", "candy_green", "candy_orange", "candy_violet", "candy_yellow"]
striped_suffix = "_STRIPED"

# Tạo dict hình ảnh
CANDY_IMAGES = {}

# Tạo hình ảnh kẹo mặc định nếu không tìm thấy file
def create_default_candy_image(color):
    surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2 - 5)
    pygame.draw.circle(surface, (255, 255, 255), (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2 - 5, 2)
    return surface

# Tạo hình ảnh kẹo mặc định cho mỗi loại
default_colors = {
    "candy_red": RED,
    "candy_blue": BLUE,
    "candy_green": GREEN,
    "candy_orange": ORANGE,
    "candy_violet": VIOLET,
    "candy_yellow": YELLOW
}

# Tạo hình ảnh mặc định cho mỗi loại kẹo
for candy_name in candies:
    CANDY_IMAGES[candy_name] = create_default_candy_image(default_colors[candy_name])
    CANDY_IMAGES[candy_name + striped_suffix] = create_default_candy_image(default_colors[candy_name])

# Tạo hình ảnh bom màu mặc định
color_bomb_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
pygame.draw.circle(color_bomb_surface, BLACK, (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2 - 5)
for i in range(8):
    angle = i * 45
    start_x, start_y = CELL_SIZE//2, CELL_SIZE//2
    end_x = start_x + int((CELL_SIZE//2 - 8) * pygame.math.Vector2(1, 0).rotate(angle).x)
    end_y = start_y + int((CELL_SIZE//2 - 8) * pygame.math.Vector2(1, 0).rotate(angle).y)
    color = default_colors[candies[i % len(candies)]]
    pygame.draw.line(color_bomb_surface, color, (start_x, start_y), (end_x, end_y), 3)
pygame.draw.circle(color_bomb_surface, WHITE, (CELL_SIZE//2, CELL_SIZE//2), 4)
CANDY_IMAGES["COLOR_BOMB"] = color_bomb_surface

# Thử tải hình ảnh từ thư mục assets
for candy_name in candies:
    # Kẹo thường
    image_path = os.path.join(ASSETS_DIR, f"{candy_name}.png")
    print(f"Candy: Đang tải ảnh kẹo từ: {image_path}")
    if os.path.exists(image_path):
        try:
            img = pygame.image.load(image_path)
            CANDY_IMAGES[candy_name] = img
            print(f"Đã tải thành công: {candy_name}")
        except Exception as e:
            print(f"Lỗi khi tải {image_path}: {e}")
    
    # Kẹo sọc (soc = striped)
    striped_path = os.path.join(ASSETS_DIR, f"{candy_name}soc.png")
    if os.path.exists(striped_path):
        try:
            img_striped = pygame.image.load(striped_path)
            img_striped = pygame.transform.scale(img_striped, (CELL_SIZE, CELL_SIZE))
            CANDY_IMAGES[candy_name + "_STRIPED_H"] = img_striped
            CANDY_IMAGES[candy_name + "_STRIPED_V"] = img_striped
            print(f"Đã tải thành công kẹo sọc: {candy_name}soc.png")
        except Exception as e:
            print(f"Lỗi khi tải {striped_path}: {e}")

    # Kẹo bọc (boc = wrapped)
    wrapped_path = os.path.join(ASSETS_DIR, f"{candy_name}boc.png")
    if os.path.exists(wrapped_path):
        try:
            img_wrapped = pygame.image.load(wrapped_path)
            img_wrapped = pygame.transform.scale(img_wrapped, (CELL_SIZE, CELL_SIZE))
            CANDY_IMAGES[candy_name + "_WRAPPED"] = img_wrapped
            print(f"Đã tải thành công kẹo bọc: {candy_name}boc.png")
        except Exception as e:
            print(f"Lỗi khi tải {wrapped_path}: {e}")

# Tải hình ảnh bom màu
try:
    color_bomb_path = os.path.join(ASSETS_DIR, "Colour_Bomb.png")
    if os.path.exists(color_bomb_path):
        color_bomb_img = pygame.image.load(color_bomb_path)
        CANDY_IMAGES["COLOR_BOMB"] = color_bomb_img
        print("Đã tải thành công: COLOR_BOMB")
except Exception as e:
    print(f"Lỗi khi tải bom màu: {e}")

print(f"Đã tải {len(CANDY_IMAGES)} hình ảnh kẹo")
for key in CANDY_IMAGES:
    print(f"  - Đã tải: {key}")


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
        
    def set_position(self, row, col):
        """Cập nhật vị trí của kẹo."""
        self.row = row
        self.col = col
        self.target_x = GRID_OFFSET_X + col * CELL_SIZE
        self.target_y = GRID_OFFSET_Y + row * CELL_SIZE    

    def update(self):
        if self.x != self.target_x or self.y != self.target_y:
            self.moving = True
    
        # Tốc độ di chuyển với gia tốc
        speed_x = max(2, abs(self.target_x - self.x) / 6)
        speed_y = max(2, abs(self.target_y - self.y) / 6)
    
        # Di chuyển theo trục X
        if abs(self.target_x - self.x) <= speed_x:
            self.x = self.target_x
        elif self.target_x > self.x:
            self.x += speed_x
        else:
            self.x -= speed_x
    
        # Di chuyển theo trục Y
        if abs(self.target_y - self.y) <= speed_y:
            self.y = self.target_y
        elif self.target_y > self.y:
            self.y += speed_y
        else:
            self.y -= speed_y
    
        # Kiểm tra xem đã đến đích chưa
        if abs(self.x - self.target_x) < 1 and abs(self.y - self.target_y) < 1:
            self.x = self.target_x
            self.y = self.target_y
            self.moving = False

    def draw(self, screen):
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
            pygame.draw.circle(screen, (139, 69, 19), (int(self.x + CELL_SIZE // 2), int(self.y + CELL_SIZE // 2)), CELL_SIZE // 3)
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x + CELL_SIZE // 2), int(self.y + CELL_SIZE // 3)), CELL_SIZE // 6)
            return

        # Xác định key ảnh dựa trên loại kẹo và loại đặc biệt
        img_key = self.candy_type.name.lower()
        if not img_key.startswith("candy_"):
            img_key = "candy_" + img_key.lower()

        # Xác định key cho kẹo đặc biệt
        special_key = None
        if self.special_type == SpecialType.STRIPED_H:
            special_key = img_key + "_STRIPED_H"
        elif self.special_type == SpecialType.STRIPED_V:
            special_key = img_key + "_STRIPED_V"
        elif self.special_type == SpecialType.WRAPPED:
            special_key = img_key + "_WRAPPED"
        elif self.special_type == SpecialType.COLOR_BOMB:
            special_key = "COLOR_BOMB"

        # Vẽ kẹo đặc biệt nếu có hình ảnh
        if special_key and special_key in CANDY_IMAGES:
            img = pygame.transform.scale(CANDY_IMAGES[special_key], (CELL_SIZE, CELL_SIZE))
            screen.blit(img, (int(self.x), int(self.y)))
        # Nếu không, vẽ kẹo thường
        elif img_key in CANDY_IMAGES:
            img = pygame.transform.scale(CANDY_IMAGES[img_key], (CELL_SIZE, CELL_SIZE))
            screen.blit(img, (int(self.x), int(self.y)))
        else:
            # dự phòng: chỉ vẽ hình tròn nếu không có hình ảnh
            pygame.draw.circle(screen, self.get_color(), (int(self.x + CELL_SIZE // 2), int(self.y + CELL_SIZE // 2)), CELL_SIZE // 2 - 5)

        # Vẽ hiệu ứng bổ sung cho kẹo đặc biệt (chỉ khi không có hình ảnh hoặc cần hiệu ứng bổ sung)
        if self.special_type != SpecialType.NORMAL:
            # Xác định key cho kẹo đặc biệt
            if self.special_type == SpecialType.STRIPED_H:
                special_key = img_key + "_STRIPED_H"
                # Vẽ hiệu ứng bổ sung nếu không có hình ảnh
                if special_key not in CANDY_IMAGES:
                    # Vẽ kẹo thường trước
                    if img_key in CANDY_IMAGES:
                        img = pygame.transform.scale(CANDY_IMAGES[img_key], (CELL_SIZE, CELL_SIZE))
                        screen.blit(img, (int(self.x), int(self.y)))
                    else:
                        pygame.draw.circle(screen, self.get_color(), (int(self.x + CELL_SIZE // 2), int(self.y + CELL_SIZE // 2)), CELL_SIZE // 2 - 5)
                    
                    # Vẽ các đường sọc ngang
                    for i in range(3):
                        y_pos = self.y + (CELL_SIZE // 4) * (i + 1)
                        pygame.draw.line(screen, WHITE, (int(self.x + 5), int(y_pos)), (int(self.x + CELL_SIZE - 5), int(y_pos)), 3)
            
            elif self.special_type == SpecialType.STRIPED_V:
                special_key = img_key + "_STRIPED_V"
                # Vẽ hiệu ứng bổ sung nếu không có hình ảnh
                if special_key not in CANDY_IMAGES:
                    # Vẽ kẹo thường trước
                    if img_key in CANDY_IMAGES:
                        img = pygame.transform.scale(CANDY_IMAGES[img_key], (CELL_SIZE, CELL_SIZE))
                        screen.blit(img, (int(self.x), int(self.y)))
                    else:
                        pygame.draw.circle(screen, self.get_color(), (int(self.x + CELL_SIZE // 2), int(self.y + CELL_SIZE // 2)), CELL_SIZE // 2 - 5)
                    
                    # Vẽ các đường sọc dọc
                    for i in range(3):
                        x_pos = self.x + (CELL_SIZE // 4) * (i + 1)
                        pygame.draw.line(screen, WHITE, (int(x_pos), int(self.y + 5)), (int(x_pos), int(self.y + CELL_SIZE - 5)), 3)
            
            elif self.special_type == SpecialType.WRAPPED:
                special_key = img_key + "_WRAPPED"
                # Nếu không có hình ảnh kẹo bọc, vẽ kẹo thường với hiệu ứng bọc
                if special_key not in CANDY_IMAGES:
                    # Vẽ kẹo thường trước
                    if img_key in CANDY_IMAGES:
                        img = pygame.transform.scale(CANDY_IMAGES[img_key], (CELL_SIZE, CELL_SIZE))
                        screen.blit(img, (int(self.x), int(self.y)))
                    else:
                        pygame.draw.circle(screen, self.get_color(), (int(self.x + CELL_SIZE // 2), int(self.y + CELL_SIZE // 2)), CELL_SIZE // 2 - 5)
                    
                    # Vẽ hiệu ứng bọc
                    pygame.draw.rect(screen, (255, 200, 0), 
                                    (int(self.x + 5), int(self.y + 5), 
                                    CELL_SIZE - 10, CELL_SIZE - 10), 
                                    3, border_radius=10)
                    
                    # Vẽ viền trong
                    pygame.draw.rect(screen, (255, 255, 0), 
                                    (int(self.x + 10), int(self.y + 10), 
                                    CELL_SIZE - 20, CELL_SIZE - 20), 
                                    2, border_radius=5)
            
            elif self.special_type == SpecialType.COLOR_BOMB:
                # Nếu không có hình ảnh bom màu, vẽ hiệu ứng
                if "COLOR_BOMB" not in CANDY_IMAGES:
                    # Vẽ nền đen cho bom màu
                    pygame.draw.circle(screen, BLACK, (int(self.x + CELL_SIZE // 2), int(self.y + CELL_SIZE // 2)), CELL_SIZE // 2 - 5)
                    
                    # Vẽ hiệu ứng lấp lánh
                    current_time = pygame.time.get_ticks()
                    for i in range(8):
                        angle = i * 45 + (current_time // 100) % 45
                        start_x, start_y = self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2
                        end_x = start_x + int((CELL_SIZE // 2 - 8) * pygame.math.Vector2(1, 0).rotate(angle).x)
                        end_y = start_y + int((CELL_SIZE // 2 - 8) * pygame.math.Vector2(1, 0).rotate(angle).y)
                        color = self.get_color_by_type(CandyType((i + (current_time // 500)) % 6))
                        pygame.draw.line(screen, color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)
                    
                    # Vẽ điểm trắng ở giữa
                    pygame.draw.circle(screen, WHITE, (int(self.x + CELL_SIZE // 2), int(self.y + CELL_SIZE // 2)), 4)

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
