import numpy as np
import heapq
from typing import List, Tuple

# --- قاعدة بيانات الأشكال الكاملة (تم استخراجها من ملف الكايلبريشن الخاص بك) ---
# دي الـ 40 شكل اللي اللعبة بتطلعهم، عشان البوت يعمل حسابه عليهم كلهم
ALL_POSSIBLE_SHAPES = [
    [(0, 0), (0, 1)],
    [(0, 0), (0, 1), (0, 2)],
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)], # 1x5 الخطير
    [(0, 0), (0, 1), (0, 2), (1, 0)],
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)],
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)], # 3x3 المربع الكبير
    [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)],
    [(0, 0), (0, 1), (0, 2), (1, 1)],
    [(0, 0), (0, 1), (0, 2), (1, 2)],
    [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)],
    [(0, 0), (0, 1), (1, 0)],
    [(0, 0), (0, 1), (1, 0), (1, 1)], # 2x2
    [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)],
    [(0, 0), (0, 1), (1, 0), (2, 0)],
    [(0, 0), (0, 1), (1, 1)],
    [(0, 0), (0, 1), (1, 1), (1, 2)],
    [(0, 0), (0, 1), (1, 1), (2, 1)],
    [(0, 0), (1, 0)],
    [(0, 0), (1, 0), (1, 1)],
    [(0, 0), (1, 0), (1, 1), (1, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 0)],
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 0), (1, 0), (2, 0), (2, 1)],
    [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)], # 5x1 العمود الطويل
    [(0, 0), (1, 1)],
    [(0, 0), (1, 1), (2, 2)],
    [(0, 1), (0, 2), (1, 0), (1, 1)],
    [(0, 1), (1, 0)],
    [(0, 1), (1, 0), (1, 1)],
    [(0, 1), (1, 0), (1, 1), (1, 2)],
    [(0, 1), (1, 0), (1, 1), (2, 0)],
    [(0, 1), (1, 0), (1, 1), (2, 1)],
    [(0, 1), (1, 1), (2, 0), (2, 1)],
    [(0, 2), (1, 0), (1, 1), (1, 2)],
    [(0, 2), (1, 1), (2, 0)],
    [(0, 2), (1, 2), (2, 0), (2, 1), (2, 2)],
]

class BlockBlastBalancedSolver:
    def __init__(self, grid_size=8):
        self.grid_size = grid_size

    def can_place(self, board: np.ndarray, shape: List[Tuple[int, int]], r: int, c: int) -> bool:
        # فحص سريع للحدود بناء على أبعد نقطة في الشكل
        if not shape: return False
        max_dr, max_dc = shape[-1] 
        if not (0 <= r + max_dr < self.grid_size and 0 <= c + max_dc < self.grid_size):
            return False
            
        for dr, dc in shape:
            if board[r + dr, c + dc] == 1:
                return False
        return True

    def place_shape(self, board: np.ndarray, shape: List[Tuple[int, int]], r: int, c: int) -> np.ndarray:
        new_board = board.copy()
        for dr, dc in shape:
            new_board[r + dr, c + dc] = 1
        return new_board

    def clear_lines(self, board: np.ndarray) -> Tuple[np.ndarray, int]:
        rows = [r for r in range(self.grid_size) if np.all(board[r, :] == 1)]
        cols = [c for c in range(self.grid_size) if np.all(board[:, c] == 1)]
        cleared = len(rows) + len(cols)
        if cleared == 0: return board, 0
        
        new_board = board.copy()
        for r in rows: new_board[r, :] = 0
        for c in cols: new_board[:, c] = 0
        return new_board, cleared

    def calculate_metrics(self, board: np.ndarray) -> dict:
        holes = 0
        roughness = 0
        peaks = []
        
        # 1. Roughness & Peaks
        for c in range(self.grid_size):
            col = board[:, c]
            if np.any(col == 1):
                pk = np.argmax(col == 1)
                height = self.grid_size - pk
            else:
                height = 0
            peaks.append(height)
        
        for i in range(len(peaks) - 1):
            roughness += abs(peaks[i] - peaks[i+1])
            
        # 2. Holes (الثقوب المحاطة بـ 4 جهات)
        padded = np.pad(board, 1, constant_values=1)
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if board[r, c] == 0:
                    neighbors = (padded[r, c+1] + padded[r+2, c+1] + 
                                 padded[r+1, c] + padded[r+1, c+2])
                    if neighbors == 4:
                        holes += 1
                        
        blocked_edges = (np.sum(board[0, :]) + np.sum(board[-1, :]) + 
                         np.sum(board[:, 0]) + np.sum(board[:, -1]))
                         
        return {'holes': holes, 'roughness': roughness, 'edges': blocked_edges}

    def calculate_survival_score(self, board: np.ndarray) -> float:
        """
        اللوجيك الجديد: حساب نسبة النجاة
        بنجرب الـ 40 شكل كلهم، وبنشوف كام واحد منهم ينفع يتحط على البورد الحالي.
        لو فيه أشكال خطيرة (زي 3x3) مش هينفع تتحط، بنخصم نقط كتير.
        """
        dangerous_shapes_missed = 0
        
        for shape in ALL_POSSIBLE_SHAPES:
            can_fit = False
            # بنجرب نحط الشكل في أي مكان
            s_rows = [p[0] for p in shape]
            s_cols = [p[1] for p in shape]
            h = max(s_rows) + 1
            w = max(s_cols) + 1
            size = len(shape)
            
            # بحث سريع عن أول مكان فاضي للشكل
            for r in range(self.grid_size - h + 1):
                for c in range(self.grid_size - w + 1):
                    valid = True
                    for dr, dc in shape:
                        if board[r+dr, c+dc] == 1:
                            valid = False; break
                    if valid:
                        can_fit = True; break
                if can_fit: break
            
            if not can_fit:
                # لو الشكل ده مش هينفع يتحط لو جالنا الدور الجاي -> خصم
                if size >= 9: # 3x3 shapes
                    dangerous_shapes_missed += 5000 # كارثة
                elif size >= 5: # 1x5 shapes
                    dangerous_shapes_missed += 2000 # خطر جدا
                else:
                    dangerous_shapes_missed += 100
                    
        return -dangerous_shapes_missed

    def calculate_combo_setup_score(self, board: np.ndarray) -> float:
        """
        مكافأة التجهيز للكومبو:
        بندور على صفوف أو عواميد فاضل فيها بلوك واحد أو اتنين وتكمل.
        """
        score = 0
        # Rows
        for r in range(self.grid_size):
            filled = np.sum(board[r, :])
            if filled == 6: score += 50   # فاضل 2
            elif filled == 7: score += 150 # فاضل 1 (ممتاز)
        # Cols
        for c in range(self.grid_size):
            filled = np.sum(board[:, c])
            if filled == 6: score += 50
            elif filled == 7: score += 150
        return score

    def evaluate_board(self, board: np.ndarray, lines_cleared: int, 
                       is_combo_secured: bool, current_combo_streak: int) -> float:
        
        metrics = self.calculate_metrics(board)
        score = 0.0
        
        # 1. العقوبات الأساسية
        score -= metrics['holes'] * 600      # الثقوب ممنوعة نهائياً
        score -= metrics['roughness'] * 40   # التعرج مسموح بيه شوية عشان الـ Setup
        
        # 2. تقييم النجاة (الأهم)
        # بدلاً من فحص 3x3 فقط، بنفحص كل الاحتمالات
        survival_penalty = self.calculate_survival_score(board)
        score += survival_penalty
        
        # 3. استراتيجية اللعب (Mode Selection)
        if not is_combo_secured and lines_cleared == 0:
            # --- HUNGRY MODE ---
            # احنا لسه معملناش Clear في الدور ده.. لازم نلاقي طريقة!
            # بنقلل تأثير العقوبات عشان نسمح بحركات "قذرة" بس بتعمل Clear
            score += 500 
        else:
            # --- SETUP MODE ---
            # ضمنا الكومبو خلاص، أو لسه عاملين Clear
            # الهدف: نجهز للدور الجاي بصفوف شبه مكتملة
            score += self.calculate_combo_setup_score(board)

        # 4. مكافأة الكومبو (سكور اللعبة)
        if lines_cleared > 0:
            combo_bonus = (current_combo_streak + 1) * 8000
            # لو الضربة دي هي اللي أنقذت الستريك، اضرب في 2
            if not is_combo_secured:
                combo_bonus *= 2 
            score += combo_bonus

        return score

    def get_valid_moves(self, board, shape):
        moves = []
        s_rows = [p[0] for p in shape]
        s_cols = [p[1] for p in shape]
        h = max(s_rows) + 1
        w = max(s_cols) + 1
        
        for r in range(self.grid_size - h + 1):
            for c in range(self.grid_size - w + 1):
                if self.can_place(board, shape, r, c):
                    moves.append((r, c))
        return moves

    def solve(self, board: np.ndarray, shapes: List[List[Tuple[int, int]]], current_game_combo: int = 0) -> List[Tuple[int, int, int]]:
        
        valid_indices = [i for i, s in enumerate(shapes) if s]
        if not valid_indices: return []

        # (Score, Counter, Bytes, Board, Path, Remaining, Streak, Secured)
        initial_secured = False 
        initial_state = (0.0, 0, board.tobytes(), board, [], valid_indices.copy(), current_game_combo, initial_secured)
        
        beam = [initial_state]
        beam_width = 20 # رقم متوازن بين السرعة والذكاء
        heap_counter = 0
        
        for step in range(len(valid_indices)):
            candidates = []
            
            for neg_score, _, _, current_board, path, remaining_indices, streak, secured in beam:
                
                if not remaining_indices:
                    # وصلنا للنهاية
                    heapq.heappush(candidates, (neg_score, heap_counter, b'', current_board, path, [], streak, secured))
                    heap_counter += 1
                    continue
                
                for i in remaining_indices:
                    shape = shapes[i]
                    valid_moves = self.get_valid_moves(current_board, shape)
                    if not valid_moves: continue
                    
                    # Optimization: لو الحركات كتيرة، نختار أفضل 8 مبدئياً عشان السرعة
                    if len(valid_moves) > 8:
                        move_priority = []
                        for r, c in valid_moves:
                            # نفضل الأطراف ونسيب النص فاضي للأشكال الكبيرة
                            dist_from_center = abs(r-3.5) + abs(c-3.5)
                            
                            # إلا لو الحركة بتعمل Clear ومحتاجين نأمن الكومبو
                            temp_board = self.place_shape(current_board, shape, r, c)
                            clears = np.any(np.all(temp_board == 1, axis=1)) or np.any(np.all(temp_board == 1, axis=0))
                            
                            prio = 1000 if (clears and not secured) else (dist_from_center * 10)
                            move_priority.append((prio, r, c))
                        
                        move_priority.sort(reverse=True)
                        valid_moves = [(r, c) for _, r, c in move_priority[:8]]

                    for r, c in valid_moves:
                        next_board = self.place_shape(current_board, shape, r, c)
                        final_board, cleared = self.clear_lines(next_board)
                        
                        new_streak = streak + 1 if cleared > 0 else 0
                        new_secured = secured or (cleared > 0)
                        
                        move_score = self.evaluate_board(final_board, cleared, secured, streak) 
                        new_total = -neg_score + move_score # (Note: score is positive is better, heap uses min so we verify sign logic)
                        # Actually in beam search usually we want Max score. 
                        # Python heapq is Min-Heap. So we store (-score).
                        # New total needs to be accumulation? 
                        # Correct logic: The beam stores (-accumulated_score).
                        # Here evaluate_board returns a "goodness" value.
                        # So we want to MAXIMIZE score.
                        # Stored value should be -score.
                        
                        new_path = path + [(i, r, c)]
                        new_remaining = [idx for idx in remaining_indices if idx != i]
                        
                        heapq.heappush(candidates, 
                                     (-new_total, heap_counter, final_board.tobytes(), 
                                      final_board, new_path, new_remaining, new_streak, new_secured))
                        heap_counter += 1
            
            if not candidates: return []
            beam = heapq.nsmallest(beam_width, candidates)
            
        if not beam: return []
        return beam[0][4]

# Wrapper for compatibility
def solve(board: np.ndarray, shapes: List[List[Tuple[int, int]]]) -> List[Tuple[int, int, int]]:
    solver = BlockBlastBalancedSolver()
    return solver.solve(board, shapes)