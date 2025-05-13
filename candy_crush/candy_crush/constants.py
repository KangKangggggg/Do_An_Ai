import pygame
import enum

# Kích thước màn hình
SCREEN_WIDTH = 850
SCREEN_HEIGHT = 750

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
VIOLET = (148, 0, 211)
ORANGE = (255, 165, 0)
BROWN = (165, 42, 42)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
PINK = (255, 192, 203)
PURPLE = (255, 0, 255)

# Kích thước lưới và ô
GRID_SIZE = 8
CELL_SIZE = 64
GRID_OFFSET_X = 100
# Tăng giá trị offset Y để di chuyển lưới xuống dưới, tạo thêm không gian cho text
GRID_OFFSET_Y = 150  # Thay đổi từ 100 lên 150

# Tham số trò chơi
ANIMATION_SPEED = 5
SWAP_ANIMATION_TIME = 0.3
MATCH_ANIMATION_TIME = 0.5

# Loại kẹo
class CandyType(enum.Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    VIOLET = 4
    ORANGE = 5

# Loại kẹo đặc biệt
class SpecialType(enum.Enum):
    NORMAL = 0
    STRIPED_H = 1  # Kẹo sọc ngang
    STRIPED_V = 2  # Kẹo sọc dọc
    WRAPPED = 3    # Kẹo dính chùm (wrapped candy)
    COLOR_BOMB = 4 # Bom màu

# Loại nút chặn
class BlockerType(enum.Enum):
    NONE = 0
    ICE = 1       # Băng
    STONE = 2     # Đá
    LOCK = 3      # Khóa
    LICORICE = 4  # Kẹo cứng
    WHITE_SPACE = 5  # Ô màu trắng

# Loại cấp độ
class LevelType(enum.Enum):
    SCORE = 0     # Cấp độ điểm
    INGREDIENT = 1 # Cấp độ nguyên liệu
    JELLY = 2     # Cấp độ kẹo dẻo
    CHOCOLATE = 3  # Cấp độ sô-cô-la

# Trạng thái trò chơi
class GameState(enum.Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    LEVEL_COMPLETE = 4
    SETTINGS = 5
    LEVEL_SELECT = 6  
    COMPARING_ALGORITHMS = 7
    
# Alias cho tương thích với code cũ
SpecialCandyType = SpecialType

# Danh sách các màu kẹo
CANDY_COLORS = [CandyType.RED, CandyType.GREEN, CandyType.BLUE, CandyType.YELLOW, CandyType.VIOLET, CandyType.ORANGE]

# Tham số hoạt hình
ANIMATION_SPEED_FACTOR = 0.8  # Hệ số tốc độ hoạt hình (thấp hơn = nhanh hơn)
GRAVITY_FACTOR = 1.2  # Hệ số trọng lực (cao hơn = rơi nhanh hơn)
SWAP_ANIMATION_SPEED = 10  # Tốc độ hoán đổi kẹo
