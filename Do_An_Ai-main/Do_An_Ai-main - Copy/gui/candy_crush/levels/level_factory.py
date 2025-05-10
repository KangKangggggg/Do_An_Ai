from .base_level import BaseLevel
from .score_level import ScoreLevel
from .jelly_level import JellyLevel
from .ingredients_level import IngredientsLevel
from .chocolate_level import ChocolateLevel
from constants import LevelType

def create_level(level_type, level_number):
    """Hàm tạo cấp độ phù hợp dựa trên loại cấp độ"""
    if level_type == LevelType.SCORE:
        return ScoreLevel(level_number)
    elif level_type == LevelType.JELLY:
        return JellyLevel(level_number)
    elif level_type == LevelType.INGREDIENT:  # Fixed: INGREDIENTS -> INGREDIENT
        return IngredientsLevel(level_number)
    elif level_type == LevelType.CHOCOLATE:
        return ChocolateLevel(level_number)
    else:
        return ScoreLevel(level_number)  # Mặc định là cấp độ điểm
