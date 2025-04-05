from enum import Enum

# Kích thước màn hình
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
GRID_SIZE = 8
CELL_SIZE = 60
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = 150
FPS = 60

# Màu sắc
WHITE = (255, 255, 255)  # Trắng
BLACK = (0, 0, 0)        # Đen
GRAY = (200, 200, 200)   # Xám
RED = (255, 50, 50)      # Đỏ
GREEN = (50, 255, 50)    # Xanh lá
BLUE = (50, 50, 255)     # Xanh dương
YELLOW = (255, 255, 50)  # Vàng
PURPLE = (255, 50, 255)  # Tím
ORANGE = (255, 150, 50)  # Cam
PINK = (255, 192, 203)   # Hồng
BROWN = (139, 69, 19)    # Nâu

# Các loại Enum
class LevelType(Enum):
    SCORE = 1       # Cấp độ điểm
    JELLY = 2       # Cấp độ kẹo dẻo
    INGREDIENTS = 3 # Cấp độ nguyên liệu
    CHOCOLATE = 4   # Cấp độ sô-cô-la

class CandyType(Enum):
    RED = 0     # Kẹo đỏ
    GREEN = 1   # Kẹo xanh lá
    BLUE = 2    # Kẹo xanh dương
    YELLOW = 3  # Kẹo vàng
    PURPLE = 4  # Kẹo tím
    ORANGE = 5  # Kẹo cam

class SpecialType(Enum):
    NORMAL = 0        # Kẹo thường
    STRIPED_H = 1     # Kẹo sọc ngang
    STRIPED_V = 2     # Kẹo sọc dọc
    WRAPPED = 3       # Kẹo bọc
    COLOR_BOMB = 4    # Bom màu

class GameState(Enum):
    MENU = 0           # Màn hình menu
    PLAYING = 1        # Đang chơi
    SWAPPING = 2       # Đang hoán đổi kẹo
    MATCHING = 3       # Đang xử lý các kẹo khớp nhau
    REFILLING = 4      # Đang điền lại kẹo mới
    GAME_OVER = 5      # Kết thúc trò chơi
    LEVEL_COMPLETE = 6 # Hoàn thành cấp độ