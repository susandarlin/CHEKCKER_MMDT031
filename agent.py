"""
AI agents for Myanmar Checkers.

* RandomAgent    -- Easy:   picks a uniformly random legal move.
* HeuristicAgent -- Medium: greedy one-ply search using the evaluation function.
* MinimaxAgent   -- Hard:   depth-limited Minimax with Alpha-Beta pruning,
                            iterative deepening and a time limit.

Every agent exposes get_move(game) -> Move and a `stats` dict describing
its last decision.
"""

import math
import random
import time

from checkers import BOARD_SIZE, EMPTY, forward_dir, is_king, owner, promotion_row

# ----------------------------------------------------------------------
# Heuristic evaluation
# ----------------------------------------------------------------------
MAN_VALUE = 100
KING_VALUE = 300          # flying kings are much stronger than men
ADVANCE_BONUS = 4         # per row a man has advanced
CENTER_BONUS = 6          # men/kings on the central squares
BACK_ROW_BONUS = 8        # men guarding their own back row
SAFE_EDGE_BONUS = 3       # pieces on a side edge cannot be jumped
MOBILITY_WEIGHT = 2       # per legal move of the side to move
THREAT_FACTOR = 0.8       # share of a pending capture's material counted now
WIN_SCORE = 100000

CENTER = {(3, 2), (3, 4), (4, 3), (4, 5), (3, 3), (4, 4), (3, 5), (4, 2)}


def evaluate(game, player):
    """Score the position from `player`'s point of view (higher is better)."""
    winner = game.get_winner()
    if winner is not None:
        if winner == 0:
            return 0
        return WIN_SCORE if winner == player else -WIN_SCORE

    score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = game.board[r][c]
            if piece == EMPTY:
                continue
            side = owner(piece)
            value = 0
            if is_king(piece):
                value += KING_VALUE
            else:
                value += MAN_VALUE
                start_row = promotion_row(-side)
                rows_advanced = abs(r - start_row)
                value += ADVANCE_BONUS * rows_advanced
                if r == start_row:
                    value += BACK_ROW_BONUS
            if (r, c) in CENTER:
                value += CENTER_BONUS
            if c == 0 or c == BOARD_SIZE - 1:
                value += SAFE_EDGE_BONUS
            score += value if side == player else -value

    # Threats / mobility of the side to move (legal moves are cached by the
    # engine). If it has a capture available, credit it with most of the best
    # capture's material, since it is mandatory and about to happen.
    # Otherwise reward mobility. Without this, a static score after our move
    # ignores pieces we have just left hanging.
    moves = game.get_legal_moves()
    captures = [m for m in moves if m.captured]
    if captures:
        swing = max(
            sum(KING_VALUE if is_king(p) else MAN_VALUE for _, _, p in m.captured)
            for m in captures
        ) * THREAT_FACTOR
    else:
        swing = MOBILITY_WEIGHT * len(moves)
    score += swing if game.current_player == player else -swing
    return score


def order_moves(moves):
    """Search captures (largest first) and promotions before quiet moves."""
    return sorted(moves, key=lambda m: (len(m.captured), m.promoted), reverse=True)


# ----------------------------------------------------------------------
# Agents
# ----------------------------------------------------------------------
class RandomAgent:
    name = "Random (Easy)"

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.stats = {}

    def get_move(self, game):
        moves = game.get_legal_moves()
        if not moves:
            return None
        move = self.rng.choice(moves)
        self.stats = {"agent": self.name, "legal_moves": len(moves)}
        return move


class HeuristicAgent:
    name = "Heuristic (Medium)"

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.stats = {}

    def get_move(self, game):
        moves = game.get_legal_moves()
        if not moves:
            return None
        player = game.current_player
        sim = game.copy()
        scored = []
        for move in moves:
            sim.make_move(move)
            scored.append((evaluate(sim, player), move))
            sim.undo_move()

        best_score = max(s for s, _ in scored)
        best = [m for s, m in scored if s == best_score]
        move = self.rng.choice(best)
        self.stats = {
            "agent": self.name,
            "legal_moves": len(moves),
            "nodes_evaluated": len(moves),
            "best_score": best_score,
            "move_scores": [{"move": m.to_dict(), "score": s} for s, m in scored],
        }
        return move


class SearchTimeout(Exception):
    pass


class MinimaxAgent:
    """
    Minimax with Alpha-Beta pruning.

    Uses iterative deepening up to `max_depth`: each finished depth replaces
    the previous answer, and if `time_limit` seconds run out mid-search the
    result of the last completed depth is used.
    """

    name = "Minimax Alpha-Beta (Hard)"

    def __init__(self, max_depth=6, time_limit=2.0):
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.stats = {}

    def get_move(self, game):
        moves = game.get_legal_moves()
        if not moves:
            return None
        if len(moves) == 1:
            self.stats = {"agent": self.name, "depth_reached": 0, "nodes_evaluated": 0,
                          "pruned": 0, "forced": True,
                          "move_scores": [{"move": moves[0].to_dict(), "score": None}]}
            return moves[0]

        self.player = game.current_player
        self.nodes = 0
        self.pruned = 0
        self.deadline = time.time() + self.time_limit
        start = time.time()

        sim = game.copy()
        best_move, best_score, move_scores, depth_reached = moves[0], None, [], 0
        root_moves = order_moves(moves)

        for depth in range(1, self.max_depth + 1):
            try:
                score, move, scores = self._search_root(sim, root_moves, depth)
            except SearchTimeout:
                break
            best_move, best_score, move_scores, depth_reached = move, score, scores, depth
            # Search the previous best move first at the next depth.
            root_moves = [move] + [m for m in root_moves if m != move]
            if abs(score) >= WIN_SCORE - 100:
                break   # forced win/loss found

        self.stats = {
            "agent": self.name,
            "depth_reached": depth_reached,
            "nodes_evaluated": self.nodes,
            "pruned": self.pruned,
            "best_score": best_score,
            "time_seconds": round(time.time() - start, 3),
            "move_scores": [{"move": m.to_dict(), "score": s} for m, s in move_scores],
        }
        return best_move

    def _search_root(self, game, moves, depth):
        alpha, beta = -math.inf, math.inf
        best_score, best_move, scores = -math.inf, moves[0], []
        for move in moves:
            game.make_move(move)
            try:
                score = self._minimax(game, depth - 1, alpha, beta, False, 1)
            finally:
                game.undo_move()
            scores.append((move, score))
            if score > best_score:
                best_score, best_move = score, move
            alpha = max(alpha, best_score)
        return best_score, best_move, scores

    def _minimax(self, game, depth, alpha, beta, maximizing, ply):
        self.nodes += 1
        if self.nodes % 512 == 0 and time.time() > self.deadline:
            raise SearchTimeout

        winner = game.get_winner()
        if winner is not None:
            if winner == 0:
                return 0
            # Prefer quicker wins and slower losses.
            return (WIN_SCORE - ply) if winner == self.player else -(WIN_SCORE - ply)
        if depth == 0:
            return evaluate(game, self.player)

        moves = order_moves(game.get_legal_moves())
        if maximizing:
            value = -math.inf
            for move in moves:
                game.make_move(move)
                try:
                    value = max(value, self._minimax(game, depth - 1, alpha, beta, False, ply + 1))
                finally:
                    game.undo_move()
                alpha = max(alpha, value)
                if alpha >= beta:
                    self.pruned += 1
                    break
            return value
        else:
            value = math.inf
            for move in moves:
                game.make_move(move)
                try:
                    value = min(value, self._minimax(game, depth - 1, alpha, beta, True, ply + 1))
                finally:
                    game.undo_move()
                beta = min(beta, value)
                if alpha >= beta:
                    self.pruned += 1
                    break
            return value


AGENTS = {
    "easy": RandomAgent,
    "medium": HeuristicAgent,
    "hard": MinimaxAgent,
}


def make_agent(difficulty):
    """Create an agent from a difficulty name: 'easy', 'medium' or 'hard'."""
    return AGENTS.get(str(difficulty).lower(), MinimaxAgent)()


if __name__ == "__main__":
    from checkers import CheckersGame, PLAYER_1, PLAYER_NAMES

    def play(red, black, max_moves=300):
        game = CheckersGame()
        while not game.is_game_over() and game.move_count < max_moves:
            agent = red if game.current_player == PLAYER_1 else black
            game.make_move(agent.get_move(game))
        return game.get_winner()

    for label, a, b in [
        ("Minimax vs Random", MinimaxAgent(max_depth=4, time_limit=0.5), RandomAgent(1)),
        ("Minimax vs Heuristic", MinimaxAgent(max_depth=4, time_limit=0.5), HeuristicAgent(1)),
        ("Heuristic vs Random", HeuristicAgent(2), RandomAgent(2)),
    ]:
        w = play(a, b)
        print(f"{label}: {PLAYER_NAMES.get(w, 'Draw/unfinished')}")
