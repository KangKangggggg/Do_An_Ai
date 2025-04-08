import pygame
import enum

# Kích thước màn hình
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BROWN = (165, 42, 42)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)

# Kích thước lưới và ô
GRID_SIZE = 8
CELL_SIZE = 60
GRID_OFFSET_X = 150
GRID_OFFSET_Y = 100

# Loại kẹo
class CandyType(enum.Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    PURPLE = 4
    ORANGE = 5

# Loại kẹo đặc biệt
class SpecialType(enum.Enum):
    NORMAL = 0
    STRIPED_H = 1  # Kẹo sọc ngang
    STRIPED_V = 2  # Kẹo sọc dọc
    WRAPPED = 3    # Kẹo bọc
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

# Trạng thái trò chơi
class GameState(enum.Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    LEVEL_COMPLETE = 4
