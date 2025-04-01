import pygame
import random
import heapq

# Khởi tạo Pygame
pygame.init()

# Cấu hình màn hình
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 8
TILE_SIZE = WIDTH // GRID_SIZE

# Màu sắc kẹo
CANDY_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]

def create_board():
    return [[random.choice(CANDY_COLORS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

board = create_board()

# Cấu hình cấp độ
levels = {
    "easy": {"moves": 30, "time": 60},
    "medium": {"moves": 20, "time": 45},
    "hard": {"moves": 10, "time": 30}
}

current_level = "easy"

# Vẽ bảng
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Candy Crush Game")

def draw_board():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pygame.draw.rect(screen, board[row][col], (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, (255, 255, 255), (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

def heuristic(board):
    """Đánh giá số kẹo có thể phá"""
    score = 0
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 2):
            if board[row][col] == board[row][col + 1] == board[row][col + 2]:
                score += 1
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE - 2):
            if board[row][col] == board[row + 1][col] == board[row + 2][col]:
                score += 1
    return score

def find_best_move():
    """Thuật toán A* tìm nước đi tốt nhất"""
    best_move = None
    best_score = 0
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            board[row][col], board[row][col + 1] = board[row][col + 1], board[row][col]
            score = heuristic(board)
            if score > best_score:
                best_score = score
                best_move = (row, col, row, col + 1)
            board[row][col], board[row][col + 1] = board[row][col + 1], board[row][col]
    return best_move

def hill_climbing():
    """Thuật toán leo đồi chọn nước đi tốt nhất"""
    best_move = find_best_move()
    if best_move:
        row1, col1, row2, col2 = best_move
        board[row1][col1], board[row2][col2] = board[row2][col2], board[row1][col1]

def main():
    running = True
    clock = pygame.time.Clock()
    
    while running:
        screen.fill((0, 0, 0))
        draw_board()
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if current_level == "easy":
            hill_climbing()
        
        clock.tick(1)  # Giảm tốc độ để xem AI hoạt động
    
    pygame.quit()

if __name__ == "__main__":
    main()
