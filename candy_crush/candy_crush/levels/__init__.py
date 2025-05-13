import sys
import os

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Make the levels package importable
from .level_factory import create_level
from .base_level import BaseLevel
from .score_level import ScoreLevel
from .jelly_level import JellyLevel
from .ingredients_level import IngredientsLevel
from .chocolate_level import ChocolateLevel

__all__ = ['BaseLevel', 'ScoreLevel', 'JellyLevel', 'IngredientsLevel', 'ChocolateLevel', 'create_level']
