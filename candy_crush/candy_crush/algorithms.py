import heapq
import random
import copy
import itertools
import math
import numpy as np
from collections import deque
from constants import *

class AIAlgorithms:
    """
    Lớp chứa các thuật toán AI để tìm nước đi tối ưu trong trò chơi Candy Crush
    """

    def __init__(self, game):
        """
        Khởi tạo với tham chiếu đến đối tượng trò chơi
        
        Tham số:
            game: Đối tượng trò chơi chính
        """
        self.game = game
        self.last_moves = []  # Lưu trữ các nước đi gần đây để tránh lặp lại
        self.max_last_moves = 5  # Số lượng nước đi gần đây cần nhớ
        self.counter = itertools.count()  # Counter for tie-breaking in heap operations
        # Khởi tạo Q-table cho Q-learning
        self.q_table = {}  # Lưu trữ giá trị Q cho trạng thái-hành động
        self.alpha = 0.1  # Tốc độ học
        self.gamma = 0.9  # Hệ số giảm giá
        self.epsilon = 0.1  # Xác suất khám phá

    def get_best_move(self, algorithm="hybrid", **kwargs):
        """
        Trả về nước đi tốt nhất sử dụng thuật toán được chỉ định
        
        Tham số:
            algorithm: "a_star", "bfs", "backtracking", "simulated_annealing", "q_learning", "and_or", hoặc "hybrid"
            **kwargs: Các tham số bổ sung cho thuật toán
                - max_depth: Độ sâu tìm kiếm tối đa
                - target_score: Điểm mục tiêu
                - iterations: Số lần lặp
                - max_temp: Nhiệt độ ban đầu cho Simulated Annealing
                
        Trả về:
            tuple: Nước đi tốt nhất dưới dạng (row1, col1, row2, col2)
        """
        if algorithm == "a_star":
            return self.a_star_search(
                max_depth=kwargs.get('max_depth', 3),
                target_score=kwargs.get('target_score', None)
            )
        elif algorithm == "bfs":
            return self.bfs_search(
                max_depth=kwargs.get('max_depth', 3)
            )
        elif algorithm == "backtracking":
            return self.backtracking_search(
                max_depth=kwargs.get('max_depth', 3),
                target_score=kwargs.get('target_score', None)
            )
        elif algorithm == "simulated_annealing":
            return self.simulated_annealing(
                max_temp=kwargs.get('max_temp', 1000),
                iterations=kwargs.get('iterations', 100)
            )
        elif algorithm == "q_learning":
            return self.q_learning_move()
        elif algorithm == "and_or":
            return self.and_or_search(
                max_depth=kwargs.get('max_depth', 3)
            )
        elif algorithm == "hybrid":
            return self.hybrid_search(
                max_depth=kwargs.get('max_depth', 2)
            )
        else:
            raise ValueError(f"Thuật toán không được hỗ trợ: {algorithm}")

    def hybrid_search(self, max_depth=2):
        """
        Kết hợp A* và Simulated Annealing để tìm nước đi tốt nhất
        
        Tham số:
            max_depth: Độ sâu tìm kiếm tối đa cho A*
            
        Trả về:
            tuple: Nước đi tốt nhất dưới dạng (row1, col1, row2, col2)
        """
        # Sử dụng A* để tìm các nước đi tốt nhất
        a_star_moves = self.get_top_moves_a_star(max_depth=max_depth, num_moves=3)
        
        # Nếu A* không tìm thấy nước đi, thử Simulated Annealing
        if not a_star_moves:
            return self.simulated_annealing(max_temp=1000, iterations=100)
        
        # Sử dụng Simulated Annealing để tinh chỉnh
        best_move = None
        best_score = -1
        
        for move in a_star_moves:
            score = self.evaluate_move(move)
            if score > best_score and move not in self.last_moves:
                best_score = score
                best_move = move
        
        # Nếu không tìm thấy nước đi tốt, thử Simulated Annealing
        if best_move is None:
            best_move = self.simulated_annealing(max_temp=1000, iterations=100)
        
        if best_move:
            self.last_moves.append(best_move)
            if len(self.last_moves) > self.max_last_moves:
                self.last_moves.pop(0)
        
        return best_move

    def bfs_search(self, max_depth=3):
        """
        Sử dụng thuật toán BFS để tìm nước đi tốt nhất
        
        Tham số:
            max_depth: Độ sâu tìm kiếm tối đa
            
        Trả về:
            tuple: Nước đi tốt nhất dưới dạng (row1, col1, row2, col2)
        """
        start_state = self._get_board_state()
        start_score = self.game.level.score
        queue = deque([([], start_state, start_score, 0)])  # (move_sequence, state, score, depth)
        visited = set([self._state_to_hashable(start_state)])
        best_move = None
        best_score_gain = -1

        while queue:
            move_sequence, state, score, depth = queue.popleft()
            
            if depth >= max_depth:
                if move_sequence:
                    move = move_sequence[0]
                    score_gain = self.evaluate_move(move)
                    if score_gain > best_score_gain and move not in self.last_moves:
                        best_score_gain = score_gain
                        best_move = move
                continue

            possible_moves = self._get_possible_moves(state)
            random.shuffle(possible_moves)

            for move in possible_moves:
                new_state, matches, score_gain = self._apply_move(state, move)
                if not matches:
                    continue

                new_score = score + score_gain
                new_move_sequence = move_sequence + [move] if move_sequence else [move]
                hashable_state = self._state_to_hashable(new_state)

                if hashable_state not in visited:
                    visited.add(hashable_state)
                    queue.append((new_move_sequence, new_state, new_score, depth + 1))

        if best_move is None:
            possible_moves = self._get_valid_moves()
            if possible_moves:
                best_move = random.choice(possible_moves)

        if best_move:
            self.last_moves.append(best_move)
            if len(self.last_moves) > self.max_last_moves:
                self.last_moves.pop(0)

        return best_move

    def backtracking_search(self, max_depth=3, target_score=None):
        """
        Sử dụng thuật toán Backtracking để tìm chuỗi nước đi tối ưu
        
        Tham số:
            max_depth: Độ sâu tìm kiếm tối đa
            target_score: Điểm mục tiêu cần đạt
            
        Trả về:
            tuple: Nước đi tốt nhất dưới dạng (row1, col1, row2, col2)
        """
        start_state = self._get_board_state()
        best_move = [None]
        best_score = [-float('inf')]

        def backtrack(state, score, depth, move_sequence):
            if depth >= max_depth or (target_score and score >= target_score):
                if move_sequence and score > best_score[0]:
                    best_score[0] = score
                    best_move[0] = move_sequence[0]
                return

            possible_moves = self._get_possible_moves(state)
            for move in possible_moves:
                new_state, matches, score_gain = self._apply_move(state, move)
                if not matches:
                    continue
                new_score = score + score_gain
                backtrack(new_state, new_score, depth + 1, move_sequence + [move] if move_sequence else [move])

        backtrack(start_state, self.game.level.score, 0, [])
        
        if best_move[0] is None:
            possible_moves = self._get_valid_moves()
            if possible_moves:
                best_move[0] = random.choice(possible_moves)

        if best_move[0]:
            self.last_moves.append(best_move[0])
            if len(self.last_moves) > self.max_last_moves:
                self.last_moves.pop(0)

        return best_move[0]

    def simulated_annealing(self, max_temp=1000, iterations=100):
        """
        Sử dụng thuật toán Simulated Annealing để tìm nước đi tốt
        
        Tham số:
            max_temp: Nhiệt độ ban đầu
            iterations: Số lần lặp
            
        Trả về:
            tuple: Nước đi tốt nhất dưới dạng (row1, col1, row2, col2)
        """
        current_move = self._get_random_move()
        current_score = self.evaluate_move(current_move)
        best_move = current_move
        best_score = current_score
        temp = max_temp

        for _ in range(iterations):
            if temp < 0.1:
                break
            neighbor_moves = self._get_neighboring_moves(current_move)
            if not neighbor_moves:
                continue
            next_move = random.choice(neighbor_moves)
            next_score = self.evaluate_move(next_move)
            delta = next_score - current_score

            if delta > 0 or random.random() < math.exp(delta / temp):
                current_move = next_move
                current_score = next_score
                if current_score > best_score and current_move not in self.last_moves:
                    best_score = current_score
                    best_move = current_move

            temp *= 0.95  # Giảm nhiệt độ

        if best_move is None or best_score <= 0:
            possible_moves = self._get_valid_moves()
            if possible_moves:
                best_move = random.choice(possible_moves)

        if best_move:
            self.last_moves.append(best_move)
            if len(self.last_moves) > self.max_last_moves:
                self.last_moves.pop(0)

        return best_move

    def q_learning_move(self):
        """
        Sử dụng Q-learning để chọn nước đi dựa trên Q-table
        
        Trả về:
            tuple: Nước đi tốt nhất dưới dạng (row1, col1, row2, col2)
        """
        state = self._state_to_hashable(self._get_board_state())
        possible_moves = self._get_valid_moves()
        
        if not possible_moves:
            return None

        # Khởi tạo Q-values cho trạng thái nếu chưa có
        if state not in self.q_table:
            self.q_table[state] = {move: 0 for move in possible_moves}

        # Epsilon-greedy selection
        if random.random() < self.epsilon:
            move = random.choice(possible_moves)
        else:
            move = max(self.q_table[state], key=self.q_table[state].get)

        # Áp dụng nước đi và nhận thưởng
        new_state, matches, reward = self._apply_move(self._get_board_state(), move)
        new_state_hash = self._state_to_hashable(new_state)
        new_possible_moves = self._get_valid_moves()

        # Khởi tạo Q-values cho trạng thái mới nếu chưa có
        if new_state_hash not in self.q_table:
            self.q_table[new_state_hash] = {m: 0 for m in new_possible_moves}

        # Cập nhật Q-value
        future_q = max(self.q_table[new_state_hash].values()) if new_possible_moves else 0
        self.q_table[state][move] += self.alpha * (
            reward + self.gamma * future_q - self.q_table[state][move]
        )

        if move:
            self.last_moves.append(move)
            if len(self.last_moves) > self.max_last_moves:
                self.last_moves.pop(0)

        return move

    def and_or_search(self, max_depth=3):
        """
        Sử dụng thuật toán AND-OR search để tìm nước đi tốt nhất
        
        Tham số:
            max_depth: Độ sâu tìm kiếm tối đa
            
        Trả về:
            tuple: Nước đi tốt nhất dưới dạng (row1, col1, row2, col2)
        """
        def and_node(state, score, depth, move_sequence):
            if depth >= max_depth:
                return score, move_sequence[0] if move_sequence else None

            possible_moves = self._get_possible_moves(state)
            best_score = -float('inf')
            best_move = None

            for move in possible_moves:
                new_state, matches, score_gain = self._apply_move(state, move)
                if not matches:
                    continue
                new_score = score + score_gain
                or_score, or_move = or_node(new_state, new_score, depth + 1, move_sequence + [move] if move_sequence else [move])
                if or_score > best_score and (not or_move or or_move not in self.last_moves):
                    best_score = or_score
                    best_move = or_move

            return best_score, best_move

        def or_node(state, score, depth, move_sequence):
            return and_node(state, score, depth, move_sequence)

        start_state = self._get_board_state()
        _, best_move = and_node(start_state, self.game.level.score, 0, [])

        if best_move is None:
            possible_moves = self._get_valid_moves()
            if possible_moves:
                best_move = random.choice(possible_moves)

        if best_move:
            self.last_moves.append(best_move)
            if len(self.last_moves) > self.max_last_moves:
                self.last_moves.pop(0)

        return best_move

    def get_top_moves_a_star(self, max_depth=2, num_moves=3):
        """
        Sử dụng A* để tìm các nước đi tốt nhất
        
        Tham số:
            max_depth: Độ sâu tìm kiếm tối đa
            num_moves: Số lượng nước đi tốt nhất cần trả về
            
        Trả về:
            list: Danh sách các nước đi tốt nhất
        """
        start_state = self._get_board_state()
        start_score = self.game.level.score
        open_set = []
        heapq.heappush(open_set, (0, next(self.counter), [], start_state, start_score, 0))
        visited = set([self._state_to_hashable(start_state)])
        best_moves = []

        while open_set and len(best_moves) < num_moves * 3:
            _, _, move_sequence, current_state, current_score, depth = heapq.heappop(open_set)
            
            if depth >= max_depth:
                if move_sequence:
                    move = move_sequence[0]
                    score = self.evaluate_move(move)
                    best_moves.append((score, move))
                continue
            
            possible_moves = self._get_possible_moves(current_state)
            random.shuffle(possible_moves)
            
            for move in possible_moves:
                new_state, matches, score_gain = self._apply_move(current_state, move)
                if not matches:
                    continue
                
                new_score = current_score + score_gain
                new_move_sequence = move_sequence + [move] if move_sequence else [move]
                h_score = -score_gain
                g_score = depth + 1
                f_score = g_score + h_score
                hashable_state = self._state_to_hashable(new_state)
                
                if hashable_state not in visited:
                    visited.add(hashable_state)
                    heapq.heappush(open_set, (f_score, next(self.counter), new_move_sequence, new_state, new_score, depth + 1))
        
        best_moves.sort(reverse=True)
        unique_moves = []
        for _, move in best_moves:
            if move not in unique_moves and move not in self.last_moves:
                unique_moves.append(move)
                if len(unique_moves) >= num_moves:
                    break
        
        return unique_moves

    def evaluate_move(self, move):
        """
        Đánh giá một nước đi dựa trên điểm số và các yếu tố khác
        
        Tham số:
            move: Nước đi cần đánh giá
            
        Trả về:
            float: Điểm đánh giá của nước đi
        """
        row1, col1, row2, col2 = move
        current_state = self._get_board_state()
        new_state, matches, score_gain = self._apply_move(current_state, move)
        
        if not matches:
            return 0
        
        score = score_gain
        
        for match in matches:
            if match["type"] == "horizontal" and match["length"] >= 4:
                score += 100
            elif match["type"] == "vertical" and match["length"] >= 4:
                score += 100
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if (current_state[row][col] and new_state[row][col] and
                    current_state[row][col].get('blocker_type', BlockerType.NONE) != BlockerType.NONE and
                    new_state[row][col].get('blocker_type', BlockerType.NONE) == BlockerType.NONE):
                    score += 50
        
        level_type = self.game.level.level_type
        if level_type == LevelType.JELLY:
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if (current_state[row][col] and new_state[row][col] and
                        current_state[row][col].get('jelly', False) and
                        not new_state[row][col].get('jelly', False)):
                        score += 75
        elif level_type == LevelType.INGREDIENT:
            for col in range(GRID_SIZE):
                for row in range(GRID_SIZE):
                    if (current_state[row][col] and current_state[row][col].get('ingredient', False) and
                        (new_state[row][col] is None or not new_state[row][col].get('ingredient', False))):
                        score += 200
        elif level_type == LevelType.CHOCOLATE:
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if (current_state[row][col] and new_state[row][col] and
                        current_state[row][col].get('chocolate', False) and
                        not new_state[row][col].get('chocolate', False)):
                        score += 100
        
        if move in self.last_moves:
            score -= 50
        
        return score

    def a_star_search(self, max_depth=3, target_score=None):
        """
        Sử dụng thuật toán A* để tìm chuỗi nước đi tối ưu
        
        Tham số:
            max_depth: Số nước đi tối đa để xem trước
            target_score: Điểm mục tiêu cần đạt
            
        Trả về:
            tuple: Nước đi tốt nhất dưới dạng (row1, col1, row2, col2)
        """
        start_state = self._get_board_state()
        start_score = self.game.level.score
        open_set = []
        heapq.heappush(open_set, (0, next(self.counter), [], start_state, start_score, 0))
        visited = set([self._state_to_hashable(start_state)])
        best_move = None
        best_score_gain = -1
        
        while open_set:
            _, _, move_sequence, current_state, current_score, depth = heapq.heappop(open_set)
            
            if (target_score and current_score >= target_score) or depth >= max_depth:
                if move_sequence:
                    return move_sequence[0]
                continue
            
            possible_moves = self._get_possible_moves(current_state)
            
            for move in possible_moves:
                new_state, matches, score_gain = self._apply_move(current_state, move)
                if not matches:
                    continue
                
                new_score = current_score + score_gain
                new_move_sequence = move_sequence + [move] if move_sequence else [move]
                h_score = target_score - new_score if target_score else -score_gain
                g_score = depth + 1
                f_score = g_score + h_score
                hashable_state = self._state_to_hashable(new_state)
                
                if hashable_state not in visited:
                    visited.add(hashable_state)
                    heapq.heappush(open_set, (f_score, next(self.counter), new_move_sequence, new_state, new_score, depth + 1))
                    
                    if score_gain > best_score_gain and move not in self.last_moves:
                        best_score_gain = score_gain
                        best_move = move
        
        if best_move is None:
            possible_moves = self._get_valid_moves()
            if possible_moves:
                best_move = random.choice(possible_moves)
        
        if best_move:
            self.last_moves.append(best_move)
            if len(self.last_moves) > self.max_last_moves:
                self.last_moves.pop(0)
        
        return best_move

    def _get_valid_moves(self):
        """Trả về tất cả các nước đi hợp lệ (tạo ra khớp) trên bảng."""
        valid_moves = []
        current_state = self._get_board_state()
        
        for row1 in range(GRID_SIZE):
            for col1 in range(GRID_SIZE):
                if col1 < GRID_SIZE - 1:
                    move = (row1, col1, row1, col1 + 1)
                    new_state, matches, _ = self._apply_move(current_state, move)
                    if matches:
                        valid_moves.append(move)
                if row1 < GRID_SIZE - 1:
                    move = (row1, col1, row1 + 1, col1)
                    new_state, matches, _ = self._apply_move(current_state, move)
                    if matches:
                        valid_moves.append(move)
        
        return valid_moves

    def _get_board_state(self):
        """Trả về một bản sao của trạng thái bảng hiện tại."""
        state = []
        for row in range(GRID_SIZE):
            state_row = []
            for col in range(GRID_SIZE):
                candy = self.game.board[row][col]
                if candy:
                    state_row.append({
                        'type': candy.candy_type,
                        'special': candy.special_type,
                        'jelly': candy.jelly,
                        'double_jelly': candy.double_jelly,
                        'chocolate': candy.chocolate,
                        'ingredient': candy.ingredient,
                        'blocker_type': candy.blocker_type,
                        'blocker_health': candy.blocker_health
                    })
                else:
                    state_row.append(None)
            state.append(state_row)
        return state

    def _state_to_hashable(self, state):
        """Chuyển đổi trạng thái bảng thành dạng có thể băm."""
        hashable = []
        for row in state:
            hashable_row = []
            for candy in row:
                if candy:
                    hashable_row.append((
                        candy['type'].value,
                        candy['special'].value,
                        candy['jelly'],
                        candy['double_jelly'],
                        candy['chocolate'],
                        candy['ingredient'],
                        candy['blocker_type'].value,
                        candy['blocker_health']
                    ))
                else:
                    hashable_row.append(None)
            hashable.append(tuple(hashable_row))
        return tuple(hashable)

    def _get_possible_moves(self, state):
        """Trả về tất cả các nước đi hợp lệ có thể trên bảng."""
        moves = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if col < GRID_SIZE - 1:
                    moves.append((row, col, row, col + 1))
                if row < GRID_SIZE - 1:
                    moves.append((row, col, row + 1, col))
        return moves

    def _get_neighboring_moves(self, move):
        """Trả về các nước đi là 'lân cận' của nước đi đã cho."""
        row1, col1, row2, col2 = move
        neighbors = []
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row1, new_col1 = row1 + dr, col1 + dc
            if 0 <= new_row1 < GRID_SIZE and 0 <= new_col1 < GRID_SIZE:
                if (new_row1, new_col1) != (row2, col2):
                    neighbors.append((new_row1, new_col1, row2, col2))
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row2, new_col2 = row2 + dr, col2 + dc
            if 0 <= new_row2 < GRID_SIZE and 0 <= new_col2 < GRID_SIZE:
                if (new_row2, new_col2) != (row1, col1):
                    neighbors.append((row1, col1, new_row2, new_col2))
        
        return neighbors

    def _apply_move(self, state, move):
        """
        Áp dụng một nước đi cho trạng thái đã cho và trả về trạng thái mới và điểm số
        """
        row1, col1, row2, col2 = move
        new_state = copy.deepcopy(state)
        new_state[row1][col1], new_state[row2][col2] = new_state[row2][col2], new_state[row1][col1]
        matches = self._find_matches(new_state)
        score_gain = 0
        
        if matches:
            matched_positions = set()
            for match in matches:
                if match["type"] == "horizontal":
                    row, col, length = match["row"], match["col"], match["length"]
                    for c in range(col, col + length):
                        matched_positions.add((row, c))
                elif match["type"] == "vertical":
                    row, col, length = match["row"], match["col"], match["length"]
                    for r in range(row, row + length):
                        matched_positions.add((r, col))
            
            score_gain = len(matched_positions) * 10
            for row, col in matched_positions:
                candy = new_state[row][col]
                if candy and candy['special'] != SpecialType.NORMAL:
                    score_gain += 20
        
        return new_state, matches, score_gain

    def _find_matches(self, state):
        """Tìm tất cả các khớp trong trạng thái đã cho."""
        matches = []
        
        for row in range(GRID_SIZE):
            col = 0
            while col < GRID_SIZE - 2:
                if (state[row][col] and state[row][col+1] and state[row][col+2] and
                    state[row][col]['type'] == state[row][col+1]['type'] == state[row][col+2]['type']):
                    match_length = 3
                    while col + match_length < GRID_SIZE and state[row][col+match_length] and state[row][col+match_length]['type'] == state[row][col]['type']:
                        match_length += 1
                    matches.append({"type": "horizontal", "row": row, "col": col, "length": match_length})
                    col += match_length
                else:
                    col += 1
        
        for col in range(GRID_SIZE):
            row = 0
            while row < GRID_SIZE - 2:
                if (state[row][col] and state[row+1][col] and state[row+2][col] and
                    state[row][col]['type'] == state[row+1][col]['type'] == state[row+2][col]['type']):
                    match_length = 3
                    while row + match_length < GRID_SIZE and state[row+match_length][col] and state[row+match_length][col]['type'] == state[row][col]['type']:
                        match_length += 1
                    matches.append({"type": "vertical", "row": row, "col": col, "length": match_length})
                    row += match_length
                else:
                    row += 1
        
        return matches

    def _get_random_move(self):
        """Trả về một nước đi hợp lệ ngẫu nhiên."""
        row1 = random.randint(0, GRID_SIZE - 1)
        col1 = random.randint(0, GRID_SIZE - 1)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        dr, dc = random.choice(directions)
        row2 = row1 + dr
        col2 = col1 + dc
        
        if 0 <= row2 < GRID_SIZE and 0 <= col2 < GRID_SIZE:
            return (row1, col1, row2, col2)
        return self._get_random_move()
