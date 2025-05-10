import pygame
import sys
from game import CandyCrushGame

def main():
    # Khởi tạo Pygame
    pygame.init()
    
    # Tạo và chạy trò chơi
    game = CandyCrushGame()
    game.run()

if __name__ == "__main__":
    main()
