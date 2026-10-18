"""
Myanmar Checkers (Kyar) game engine.

Rules implemented
-----------------
* 8x8 board, play only on dark squares ((row + col) % 2 == 1).
* Each player starts with 12 men on the dark squares of the three rows
  nearest to them. Player 1 (RED) sits at the bottom (rows 5-7) and moves
  first; Player 2 (BLACK) sits at the top (rows 0-2).
* Men move one square diagonally forward and capture forward only, by
  jumping over an adjacent enemy piece onto the empty square beyond it.
* A man that reaches the far row is promoted to a king. Promotion ends the
  turn, even in the middle of a capture sequence.
* Kings are "flying": they move any distance diagonally (forward or
  backward) over empty squares, and capture an enemy piece at any distance
  on a diagonal, landing on any empty square beyond it.
* Multi-jump: after a capture, if the same piece can capture again it must
  continue. Captured pieces are removed only at the end of the sequence and
  cannot be jumped twice.
* Captures are mandatory (set MANDATORY_CAPTURE = False to make them
  optional).
* A player with no pieces or no legal moves loses.
* Draw: NO_PROGRESS_LIMIT moves in a row without a capture or a man move,
  or the same position (with the same side to move) occurring
  REPETITION_LIMIT times.

Board encoding
--------------
board[row][col] holds one of EMPTY, P1_MAN, P1_KING, P2_MAN, P2_KING.
Positive values belong to Player 1, negative to Player 2, so
`piece * player > 0` means "piece belongs to player".
"""

BOARD_SIZE = 8
START_ROWS = 3

EMPTY = 0
P1_MAN = 1
P1_KING = 2
P2_MAN = -1
P2_KING = -2

PLAYER_1 = 1    # RED, bottom, moves "up" (row decreases)
PLAYER_2 = -1   # BLACK, top, moves "down" (row increases)

PLAYER_NAMES = {PLAYER_1: "Red", PLAYER_2: "Black"}

MANDATORY_CAPTURE = True
NO_PROGRESS_LIMIT = 50
REPETITION_LIMIT = 3

DIAGONALS = ((-1, -1), (-1, 1), (1, -1), (1, 1))


def owner(piece):
    """Return the player owning a piece, or 0 for an empty square."""
    if piece > 0:
        return PLAYER_1
    if piece < 0:
        return PLAYER_2
    return 0


def is_king(piece):
    return abs(piece) == 2


def forward_dir(player):
    """Row direction in which a player's men advance."""
    return -1 if player == PLAYER_1 else 1


def promotion_row(player):
    return 0 if player == PLAYER_1 else BOARD_SIZE - 1


def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


class Move:
    """
    A complete move (a simple step or a full capture sequence).

    path      -- list of (row, col) squares visited, starting square first
    captured  -- list of (row, col, piece) for every piece jumped
    promoted  -- True if the moving man became a king
    """

    __slots__ = ("path", "captured", "promoted", "piece")

    def __init__(self, path, captured=None, promoted=False, piece=EMPTY):
        self.path = list(path)
        self.captured = list(captured) if captured else []
        self.promoted = promoted
        self.piece = piece

    @property
    def start(self):
        return self.path[0]

    @property
    def end(self):
        return self.path[-1]

    @property
    def is_capture(self):
        return bool(self.captured)

    def to_dict(self):
        return {
            "path": [list(sq) for sq in self.path],
            "from": list(self.start),
            "to": list(self.end),
            "captured": [[r, c] for r, c, _ in self.captured],
            "promoted": self.promoted,
        }

    def __eq__(self, other):
        return isinstance(other, Move) and self.path == other.path

    def __hash__(self):
        return hash(tuple(self.path))

    def __repr__(self):
        sep = "x" if self.captured else "-"
        return "Move(" + sep.join(f"{r},{c}" for r, c in self.path) + ")"


class CheckersGame:
    """Game state with move generation, execution, undo and result checks."""

    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    # Setup / state
    # ------------------------------------------------------------------
    def reset(self):
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if (r + c) % 2 == 0:
                    continue
                if r < START_ROWS:
                    self.board[r][c] = P2_MAN
                elif r >= BOARD_SIZE - START_ROWS:
                    self.board[r][c] = P1_MAN
        self.current_player = PLAYER_1
        self.no_progress_count = 0
        self.move_count = 0
        self.history = []                 # undo stack
        self.position_counts = {}
        self._record_position()
        self._legal_cache = None

    def copy(self):
        g = CheckersGame.__new__(CheckersGame)
        g.board = [row[:] for row in self.board]
        g.current_player = self.current_player
        g.no_progress_count = self.no_progress_count
        g.move_count = self.move_count
        g.history = list(self.history)
        g.position_counts = dict(self.position_counts)
        g._legal_cache = None
        return g

    def position_key(self):
        return (tuple(tuple(row) for row in self.board), self.current_player)

    def _record_position(self):
        key = self.position_key()
        self.position_counts[key] = self.position_counts.get(key, 0) + 1

    def _unrecord_position(self):
        key = self.position_key()
        n = self.position_counts.get(key, 0) - 1
        if n > 0:
            self.position_counts[key] = n
        else:
            self.position_counts.pop(key, None)

    def pieces(self, player):
        """List of (row, col, piece) owned by player."""
        return [
            (r, c, p)
            for r, row in enumerate(self.board)
            for c, p in enumerate(row)
            if p * player > 0
        ]

    def count_pieces(self, player):
        """Return (men, kings) for player."""
        men = kings = 0
        for row in self.board:
            for p in row:
                if p * player > 0:
                    if is_king(p):
                        kings += 1
                    else:
                        men += 1
        return men, kings

    # ------------------------------------------------------------------
    # Move generation
    # ------------------------------------------------------------------
    def get_legal_moves(self, player=None):
        if player is None or player == self.current_player:
            if self._legal_cache is None:
                self._legal_cache = self._generate_moves(self.current_player)
            return list(self._legal_cache)
        return self._generate_moves(player)

    def _generate_moves(self, player):
        captures, steps = [], []
        for r, c, piece in self.pieces(player):
            captures.extend(self._capture_moves(r, c, piece, player))
            if not (MANDATORY_CAPTURE and captures):
                steps.extend(self._step_moves(r, c, piece, player))
        if MANDATORY_CAPTURE and captures:
            return captures
        return captures + steps

    def _step_moves(self, r, c, piece, player):
        moves = []
        if is_king(piece):
            for dr, dc in DIAGONALS:
                nr, nc = r + dr, c + dc
                while in_bounds(nr, nc) and self.board[nr][nc] == EMPTY:
                    moves.append(Move([(r, c), (nr, nc)], piece=piece))
                    nr += dr
                    nc += dc
        else:
            dr = forward_dir(player)
            for dc in (-1, 1):
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc) and self.board[nr][nc] == EMPTY:
                    promoted = nr == promotion_row(player)
                    moves.append(Move([(r, c), (nr, nc)], promoted=promoted, piece=piece))
        return moves

    def _capture_moves(self, r, c, piece, player):
        """All complete capture sequences for the piece at (r, c)."""
        results = []
        # Lift the moving piece so its start square counts as empty.
        self.board[r][c] = EMPTY
        try:
            self._extend_capture(r, c, piece, player, [(r, c)], [], results)
        finally:
            self.board[r][c] = piece
        return results

    def _jumps_from(self, r, c, piece, player, captured_squares):
        """Single jumps available from (r, c): list of (land_sq, captured_sq)."""
        jumps = []
        if is_king(piece):
            for dr, dc in DIAGONALS:
                nr, nc = r + dr, c + dc
                while in_bounds(nr, nc) and self.board[nr][nc] == EMPTY:
                    nr += dr
                    nc += dc
                if not in_bounds(nr, nc):
                    continue
                target = self.board[nr][nc]
                if owner(target) != -player or (nr, nc) in captured_squares:
                    continue
                lr, lc = nr + dr, nc + dc
                while in_bounds(lr, lc) and self.board[lr][lc] == EMPTY:
                    jumps.append(((lr, lc), (nr, nc)))
                    lr += dr
                    lc += dc
        else:
            dr = forward_dir(player)
            for dc in (-1, 1):
                mr, mc = r + dr, c + dc
                lr, lc = r + 2 * dr, c + 2 * dc
                if not in_bounds(lr, lc):
                    continue
                if (owner(self.board[mr][mc]) == -player
                        and (mr, mc) not in captured_squares
                        and self.board[lr][lc] == EMPTY):
                    jumps.append(((lr, lc), (mr, mc)))
        return jumps

    def _extend_capture(self, r, c, piece, player, path, captured, results):
        captured_squares = {(cr, cc) for cr, cc, _ in captured}
        jumps = self._jumps_from(r, c, piece, player, captured_squares)
        if not jumps:
            if captured:
                results.append(Move(path, captured, piece=piece))
            return
        for (lr, lc), (cr, cc) in jumps:
            new_path = path + [(lr, lc)]
            new_captured = captured + [(cr, cc, self.board[cr][cc])]
            if not is_king(piece) and lr == promotion_row(player):
                # Promotion ends the turn immediately.
                results.append(Move(new_path, new_captured, promoted=True, piece=piece))
            else:
                self._extend_capture(lr, lc, piece, player, new_path, new_captured, results)

    def find_move(self, path):
        """Match a path (list of [row, col]) from the UI to a legal move.

        A two-square path [from, to] also matches a multi-jump with the
        same start and end, provided exactly one such move exists.
        """
        path = [tuple(sq) for sq in path]
        legal = self.get_legal_moves()
        for m in legal:
            if m.path == path:
                return m
        if len(path) == 2:
            matches = [m for m in legal if m.start == path[0] and m.end == path[1]]
            if len(matches) == 1:
                return matches[0]
        return None

    # ------------------------------------------------------------------
    # Move execution / undo
    # ------------------------------------------------------------------
    def make_move(self, move):
        (sr, sc), (er, ec) = move.start, move.end
        piece = self.board[sr][sc]
        if owner(piece) != self.current_player:
            raise ValueError(f"No {PLAYER_NAMES[self.current_player]} piece at {move.start}")

        self.history.append((move, piece, self.no_progress_count))

        self.board[sr][sc] = EMPTY
        for cr, cc, _ in move.captured:
            self.board[cr][cc] = EMPTY
        self.board[er][ec] = (2 * self.current_player) if move.promoted else piece

        if move.captured or not is_king(piece):
            self.no_progress_count = 0
        else:
            self.no_progress_count += 1

        self.move_count += 1
        self.current_player = -self.current_player
        self._legal_cache = None
        self._record_position()

    def undo_move(self):
        if not self.history:
            raise IndexError("No moves to undo")
        self._unrecord_position()
        move, piece, prev_no_progress = self.history.pop()
        (sr, sc), (er, ec) = move.start, move.end

        self.board[er][ec] = EMPTY
        for cr, cc, captured_piece in move.captured:
            self.board[cr][cc] = captured_piece
        self.board[sr][sc] = piece

        self.no_progress_count = prev_no_progress
        self.move_count -= 1
        self.current_player = -self.current_player
        self._legal_cache = None
        return move

    # ------------------------------------------------------------------
    # Game result
    # ------------------------------------------------------------------
    def is_draw(self):
        if self.no_progress_count >= NO_PROGRESS_LIMIT:
            return True
        return self.position_counts.get(self.position_key(), 0) >= REPETITION_LIMIT

    def get_winner(self):
        """PLAYER_1 / PLAYER_2 if the game is won, 0 for a draw, None if ongoing."""
        if not self.get_legal_moves():
            return -self.current_player
        if self.is_draw():
            return 0
        return None

    def is_game_over(self):
        return self.get_winner() is not None

    def result_message(self):
        winner = self.get_winner()
        if winner is None:
            return f"{PLAYER_NAMES[self.current_player]} to move"
        if winner == 0:
            return "Draw"
        return f"{PLAYER_NAMES[winner]} wins"

    # ------------------------------------------------------------------
    # Serialisation / display
    # ------------------------------------------------------------------
    def to_dict(self):
        winner = self.get_winner()
        return {
            "board": [row[:] for row in self.board],
            "current_player": self.current_player,
            "legal_moves": [m.to_dict() for m in self.get_legal_moves()],
            "game_over": winner is not None,
            "winner": winner,
            "status": self.result_message(),
            "move_count": self.move_count,
            "last_move": self.history[-1][0].to_dict() if self.history else None,
        }

    def __str__(self):
        symbols = {EMPTY: ".", P1_MAN: "r", P1_KING: "R", P2_MAN: "b", P2_KING: "B"}
        lines = ["  " + " ".join(str(c) for c in range(BOARD_SIZE))]
        for r, row in enumerate(self.board):
            cells = []
            for c, p in enumerate(row):
                cells.append(symbols[p] if (r + c) % 2 else " ")
            lines.append(f"{r} " + " ".join(cells))
        return "\n".join(lines)


if __name__ == "__main__":
    import random

    game = CheckersGame()
    print(game)
    while not game.is_game_over():
        game.make_move(random.choice(game.get_legal_moves()))
    print()
    print(game)
    print(game.result_message(), "after", game.move_count, "moves")
