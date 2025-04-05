from .base_level import BaseLevel
from constants import LevelType

class ScoreLevel(BaseLevel):
    def __init__(self, level_number):
        super().__init__(level_number)
        self.level_type = LevelType.SCORE
        self.target_score = 1000 * level_number
    
    def initialize(self):
        super().initialize()
    
    def is_level_complete(self):
        return self.score >= self.target_score