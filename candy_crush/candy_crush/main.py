import pygame
import sys
import os

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from game import CandyCrushGame

def main():
    # Khởi tạo Pygame
    pygame.init()
    
    # Khởi tạo âm thanh
    try:
        pygame.mixer.init()
        print("Hệ thống âm thanh đã được khởi tạo thành công")
    except:
        print("Không thể khởi tạo hệ thống âm thanh")
    
    # Tạo và chạy trò chơi
    game = CandyCrushGame()
    game.run()

if __name__ == "__main__":
    main()
