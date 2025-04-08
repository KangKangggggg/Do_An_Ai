import pygame
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .game import CandyCrushGame


def main():
    # Initialize Pygame
    pygame.init()
    
    # Create and run the game
    game = CandyCrushGame()
    game.run()

if __name__ == "__main__":
    main()