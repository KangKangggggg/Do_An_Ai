from .base_level import BaseLevel
from constants import LevelType

class ScoreLevel(BaseLevel):
    def __init__(self, level_number):
        super().__init__(level_number)
        self.level_type = LevelType.SCORE
        # Giảm điểm mục tiêu thêm nữa
        self.target_score = 600 * level_number
    
    def initialize(self):
        super().initialize()
        # Don't reset moves_left here
    
    def is_level_complete(self):
        return self.score >= self.target_score
