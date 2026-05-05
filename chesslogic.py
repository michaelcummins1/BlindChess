"""
Blind Chess Logic
Self-contained chess logic. ChessGame class.

INTERFACE CONTRACT (for voice recognition / UI layer):
    game = ChessGame()
    result = game.handle_command(command_string)
    # result is always a CommandResult dataclass

CommandResult:
    success: bool
    type: str        # "move" | "reveal" | "hide" | "neighbors" | "forfeit"
                     # "start" | "error" | "status"
    message: str     # human-readable string ready for TTS / display
    state: GameState # current game state snapshot

GameState:
    turn: str              # "white" | "black"
    status: str            # "waiting" | "active" | "check" | "checkmate"
                           #  "stalemate" | "forfeit"
    winner: str | None     # "white" | "black" | None
    board_visible: bool
    board: list[list]      # 8x8, each cell None or {"piece": str, "color": str}

RECOGNIZED COMMAND STRINGS (passed in by voice recognition layer):
    "start game"
    "e2 to e4" / "pawn e2 to e4" / "e2e4"      <- move formats
    "reveal board" / "show board"
    "hide board"
    "queen's neighbors" / "neighbors of e4"
    "end game by forfeit" / "forfeit"
    "check status"
    "castle kingside" / "castle queenside" / "castling"
"""

import re
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PIECES = {
    "KING":   "king",
    "QUEEN":  "queen",
    "ROOK":   "rook",
    "BISHOP": "bishop",
    "KNIGHT": "knight",
    "PAWN":   "pawn",
}

WHITE = "white"
BLACK = "black"

PIECE_ALIASES = {
    "king": "king",   "k": "king",
    "queen": "queen", "q": "queen",
    "rook": "rook",   "r": "rook",
    "bishop": "bishop", "b": "bishop",
    "knight": "knight", "n": "knight", "horse": "knight",
    "pawn": "pawn",   "p": "pawn",
}

BACK_RANK = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]

SQUARE_RE = re.compile(r"[a-h][1-8]")


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class GameState:
    turn: str
    status: str
    winner: Optional[str]
    board_visible: bool
    board: list  # 8x8 list of dicts or None


@dataclass
class CommandResult:
    success: bool
    type: str
    message: str
    state: GameState


# ---------------------------------------------------------------------------
# Board Utilities
# ---------------------------------------------------------------------------

def file_to_col(file: str) -> int:
    return ord(file) - ord("a")

def rank_to_row(rank: str) -> int:
    return 8 - int(rank)

def col_to_file(col: int) -> str:
    return chr(ord("a") + col)

def row_to_rank(row: int) -> str:
    return str(8 - row)

def square_to_coords(sq: str) -> Optional[tuple]:
    sq = sq.strip().lower()
    if len(sq) != 2:
        return None
    col = file_to_col(sq[0])
    row = rank_to_row(sq[1])
    if not (0 <= col <= 7 and 0 <= row <= 7):
        return None
    return (row, col)

def coords_to_square(row: int, col: int) -> str:
    return col_to_file(col) + row_to_rank(row)

def in_bounds(row: int, col: int) -> bool:
    return 0 <= row < 8 and 0 <= col < 8

def make_piece(piece: str, color: str) -> dict:
    return {"piece": piece, "color": color}


# ---------------------------------------------------------------------------
# Initial Board Setup
# ---------------------------------------------------------------------------

def create_initial_board() -> list:
    board = [[None] * 8 for _ in range(8)]
    for col, piece in enumerate(BACK_RANK):
        board[0][col] = make_piece(piece, BLACK)
        board[1][col] = make_piece("pawn", BLACK)
        board[6][col] = make_piece("pawn", WHITE)
        board[7][col] = make_piece(piece, WHITE)
    return board


# ---------------------------------------------------------------------------
# Move Generation
# ---------------------------------------------------------------------------

def get_pseudo_legal_moves(board, row, col, en_passant_target, castling_rights) -> list:
    """
    Returns list of dicts: {"row": int, "col": int, "special": str|None}
    Does NOT filter for self-check.
    """
    cell = board[row][col]
    if not cell:
        return []

    piece = cell["piece"]
    color = cell["color"]
    opp = BLACK if color == WHITE else WHITE
    moves = []

    def slide(dr, dc):
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            if board[r][c]:
                if board[r][c]["color"] == opp:
                    moves.append({"row": r, "col": c, "special": None})
                break
            moves.append({"row": r, "col": c, "special": None})
            r += dr
            c += dc

    def step(dr, dc):
        r, c = row + dr, col + dc
        if in_bounds(r, c) and (not board[r][c] or board[r][c]["color"] != color):
            moves.append({"row": r, "col": c, "special": None})

    if piece == "rook":
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            slide(dr, dc)

    elif piece == "bishop":
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            slide(dr, dc)

    elif piece == "queen":
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            slide(dr, dc)

    elif piece == "king":
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                       (0, 1), (1, -1), (1, 0), (1, 1)]:
            step(dr, dc)
        # Castling
        base_row = 7 if color == WHITE else 0
        if row == base_row and col == 4:
            cr = castling_rights[color]
            # Kingside
            if (cr["kingside"]
                    and not board[base_row][5]
                    and not board[base_row][6]
                    and board[base_row][7]
                    and board[base_row][7]["piece"] == "rook"
                    and board[base_row][7]["color"] == color):
                moves.append({"row": base_row, "col": 6, "special": "castle_kingside"})
            # Queenside
            if (cr["queenside"]
                    and not board[base_row][3]
                    and not board[base_row][2]
                    and not board[base_row][1]
                    and board[base_row][0]
                    and board[base_row][0]["piece"] == "rook"
                    and board[base_row][0]["color"] == color):
                moves.append({"row": base_row, "col": 2, "special": "castle_queenside"})

    elif piece == "knight":
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]:
            step(dr, dc)

    elif piece == "pawn":
        direction = -1 if color == WHITE else 1
        start_row = 6 if color == WHITE else 1
        # Forward
        r = row + direction
        if in_bounds(r, col) and not board[r][col]:
            moves.append({"row": r, "col": col, "special": None})
            # Double push from start row
            rr = row + 2 * direction
            if row == start_row and not board[rr][col]:
                moves.append({"row": rr, "col": col, "special": "double_push"})
        # Diagonal captures
        for dc in [-1, 1]:
            r, c = row + direction, col + dc
            if not in_bounds(r, c):
                continue
            if board[r][c] and board[r][c]["color"] == opp:
                moves.append({"row": r, "col": c, "special": None})
            # En passant
            if (en_passant_target
                    and en_passant_target[0] == r
                    and en_passant_target[1] == c):
                moves.append({"row": r, "col": c, "special": "en_passant"})

    return moves


# ---------------------------------------------------------------------------
# Check Detection
# ---------------------------------------------------------------------------

def is_square_attacked(board, row, col, by_color) -> bool:
    no_castle = {WHITE: {"kingside": False, "queenside": False},
                 BLACK: {"kingside": False, "queenside": False}}
    for r in range(8):
        for c in range(8):
            cell = board[r][c]
            if not cell or cell["color"] != by_color:
                continue
            moves = get_pseudo_legal_moves(board, r, c, None, no_castle)
            if any(m["row"] == row and m["col"] == col for m in moves):
                return True
    return False


def find_king(board, color) -> Optional[tuple]:
    for r in range(8):
        for c in range(8):
            cell = board[r][c]
            if cell and cell["piece"] == "king" and cell["color"] == color:
                return (r, c)
    return None


def is_in_check(board, color) -> bool:
    king = find_king(board, color)
    if not king:
        return False
    opp = BLACK if color == WHITE else WHITE
    return is_square_attacked(board, king[0], king[1], opp)


# ---------------------------------------------------------------------------
# Move Application
# ---------------------------------------------------------------------------

def apply_move(board, from_row, from_col, to_row, to_col, special,
               castling_rights, promotion_piece="queen") -> dict:
    """
    Returns dict with keys:
        board, captured_piece, promotion_occurred,
        en_passant_target, castling_rights
    Original board is NOT mutated.
    """
    new_board = deepcopy(board)
    moving = new_board[from_row][from_col]
    captured_piece = new_board[to_row][to_col]["piece"] if new_board[to_row][to_col] else None
    en_passant_target = None

    if special == "en_passant":
        captured_piece = new_board[from_row][to_col]["piece"] if new_board[from_row][to_col] else None
        new_board[from_row][to_col] = None

    if special == "double_push":
        ep_row = (from_row + to_row) // 2
        en_passant_target = (ep_row, to_col)

    if special == "castle_kingside":
        new_board[to_row][5] = new_board[to_row][7]
        new_board[to_row][7] = None

    if special == "castle_queenside":
        new_board[to_row][3] = new_board[to_row][0]
        new_board[to_row][0] = None

    new_board[to_row][to_col] = moving
    new_board[from_row][from_col] = None

    # Pawn promotion
    promotion_occurred = False
    if moving["piece"] == "pawn" and to_row in (0, 7):
        new_board[to_row][to_col] = make_piece(promotion_piece, moving["color"])
        promotion_occurred = True

    # Update castling rights
    new_cr = deepcopy(castling_rights)
    color = moving["color"]
    opp = BLACK if color == WHITE else WHITE

    if moving["piece"] == "king":
        new_cr[color]["kingside"] = False
        new_cr[color]["queenside"] = False
    if moving["piece"] == "rook":
        if from_col == 7:
            new_cr[color]["kingside"] = False
        if from_col == 0:
            new_cr[color]["queenside"] = False
    if captured_piece == "rook":
        if to_col == 7:
            new_cr[opp]["kingside"] = False
        if to_col == 0:
            new_cr[opp]["queenside"] = False

    return {
        "board": new_board,
        "captured_piece": captured_piece,
        "promotion_occurred": promotion_occurred,
        "en_passant_target": en_passant_target,
        "castling_rights": new_cr,
    }


# ---------------------------------------------------------------------------
# Legal Move Validation
# ---------------------------------------------------------------------------

def is_legal_move(board, from_row, from_col, to_row, to_col,
                  special, castling_rights, en_passant_target) -> bool:
    cell = board[from_row][from_col]
    if not cell:
        return False

    color = cell["color"]
    opp = BLACK if color == WHITE else WHITE

    if special in ("castle_kingside", "castle_queenside"):
        if is_in_check(board, color):
            return False
        base_row = 7 if color == WHITE else 0
        pass_cols = [5, 6] if special == "castle_kingside" else [3, 2]
        for c in pass_cols:
            if is_square_attacked(board, base_row, c, opp):
                return False

    result = apply_move(board, from_row, from_col, to_row, to_col,
                        special, castling_rights)
    return not is_in_check(result["board"], color)


def get_all_legal_moves(board, color, castling_rights, en_passant_target) -> list:
    moves = []
    for r in range(8):
        for c in range(8):
            if not board[r][c] or board[r][c]["color"] != color:
                continue
            pseudo = get_pseudo_legal_moves(board, r, c, en_passant_target, castling_rights)
            for m in pseudo:
                if is_legal_move(board, r, c, m["row"], m["col"],
                                 m["special"], castling_rights, en_passant_target):
                    moves.append({"from_row": r, "from_col": c, **m})
    return moves


# ---------------------------------------------------------------------------
# Command Parsing
# ---------------------------------------------------------------------------

def parse_move(text: str) -> Optional[dict]:
    norm = text.lower()
    norm = re.sub(r"\bto\b", " ", norm)
    norm = re.sub(r"\bfrom\b", " ", norm)
    norm = re.sub(r"\s+", " ", norm).strip()

    squares = SQUARE_RE.findall(norm)

    if re.search(r"castle\s*king\s*side|king\s*side\s*castle", norm) or norm == "o-o":
        return {"type": "castle_kingside"}
    if re.search(r"castle\s*queen\s*side|queen\s*side\s*castle", norm) or norm == "o-o-o":
        return {"type": "castle_queenside"}
    if re.search(r"\bcastl", norm) and not squares:
        return {"type": "castle_kingside"}

    if len(squares) >= 2:
        return {"type": "move", "from": squares[0].lower(), "to": squares[1].lower()}

    return None


def parse_neighbor_query(text: str) -> Optional[dict]:
    norm = text.lower()
    squares = SQUARE_RE.findall(norm)
    if squares:
        return {"query_type": "square", "value": squares[0].lower()}
    for alias, canonical in PIECE_ALIASES.items():
        if alias in norm.split() or f"{alias}'s" in norm or f"{alias}s" in norm:
            return {"query_type": "piece", "value": canonical}
    # Fallback: substring match
    for alias, canonical in sorted(PIECE_ALIASES.items(), key=lambda x: -len(x[0])):
        if alias in norm:
            return {"query_type": "piece", "value": canonical}
    return None


# ---------------------------------------------------------------------------
# Neighbor Queries
# ---------------------------------------------------------------------------

def describe_neighbors(board, color, query) -> dict:
    candidates = []
    for r in range(8):
        for c in range(8):
            cell = board[r][c]
            if not cell or cell["color"] != color:
                continue
            if query["query_type"] == "square":
                coords = square_to_coords(query["value"])
                if coords and coords == (r, c):
                    candidates.append((r, c, cell))
            elif query["query_type"] == "piece":
                if cell["piece"] == query["value"]:
                    candidates.append((r, c, cell))

    if not candidates:
        return {"success": False,
                "message": f"No {color} piece found matching that query."}

    messages = []
    for r, c, cell in candidates:
        sq = coords_to_square(r, c)
        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if not in_bounds(nr, nc):
                    continue
                neighbor_cell = board[nr][nc]
                neighbors.append({
                    "square": coords_to_square(nr, nc),
                    "occupant": neighbor_cell,
                })
        occupied = [n for n in neighbors if n["occupant"]]
        if not occupied:
            messages.append(f"{cell['piece']} on {sq} has no neighboring pieces.")
        else:
            desc = ", ".join(
                f"{n['occupant']['color']} {n['occupant']['piece']} on {n['square']}"
                for n in occupied
            )
            messages.append(f"{cell['piece']} on {sq}: neighboring pieces are {desc}.")

    return {"success": True, "message": " ".join(messages)}


# ---------------------------------------------------------------------------
# Move Description Builder
# ---------------------------------------------------------------------------

def build_move_description(piece, from_sq, to_sq, captured_piece, special,
                            promotion_occurred) -> str:
    if special == "castle_kingside":
        return "Kingside castling occurred."
    if special == "castle_queenside":
        return "Queenside castling occurred."
    msg = f"{piece} moved from {from_sq} to {to_sq}"
    if captured_piece:
        msg += f", capturing {captured_piece}"
    if promotion_occurred:
        msg += ", promoted to queen"
    return msg + "."


# ---------------------------------------------------------------------------
# ChessGame — Main Class
# ---------------------------------------------------------------------------

class ChessGame:
    """
    Main chess engine class. All interaction goes through handle_command().

    Example usage:
        game = ChessGame()
        result = game.handle_command("start game")
        result = game.handle_command("e2 to e4")
        result = game.handle_command("reveal board")
        result = game.handle_command("queen's neighbors")
        print(result.message)   # ready for TTS
        print(result.state.turn)
    """

    def __init__(self):
        self._reset()

    # ---- Public API --------------------------------------------------------

    def handle_command(self, text: str) -> CommandResult:
        """
        Main entry point. Accepts any recognized command string.
        Always returns a CommandResult — never raises.
        """
        norm = text.strip().lower()

        # Start game
        if re.search(r"\bstart\b.*\bgame\b|\bnew\s+game\b", norm):
            return self._start_game()

        # Forfeit
        if re.search(r"\bforfeit\b|\bend\s+game\b", norm):
            return self._forfeit()

        # Game must be active for all remaining commands
        if self.status == "waiting":
            return self._result(False, "error",
                                "Game not started. Say 'start game' to begin.")
        if self.status in ("checkmate", "stalemate", "forfeit"):
            return self._result(False, "error",
                                "The game is over. Say 'start game' to play again.")

        # Reveal board
        if re.search(r"\breveal\b|\bshow\b.*\bboard\b|\bdisplay\b.*\bboard\b", norm):
            self.board_visible = True
            return self._result(True, "reveal", "Board revealed.")

        # Hide board
        if re.search(r"\bhide\b.*\bboard\b|\bconceal\b.*\bboard\b", norm):
            self.board_visible = False
            return self._result(True, "hide", "Board hidden.")

        # Neighbor query
        if "neighbor" in norm:
            query = parse_neighbor_query(norm)
            if not query:
                return self._result(False, "error",
                                    "Could not understand neighbor query. "
                                    "Please specify a piece or square.")
            result = describe_neighbors(self.board, self.turn, query)
            return self._result(result["success"], "neighbors", result["message"])

        # Check status query
        if re.search(r"\bcheck\s+status\b|\bam\s+i\s+in\s+check\b", norm):
            in_check = is_in_check(self.board, self.turn)
            msg = (f"{self.turn}'s king is in check."
                   if in_check else f"{self.turn}'s king is not in check.")
            return self._result(True, "status", msg)

        # Castling shorthand
        if re.search(r"\bcastl", norm) and "neighbor" not in norm:
            parsed = parse_move(norm)
            if parsed and parsed["type"] in ("castle_kingside", "castle_queenside"):
                return self._attempt_castle(parsed["type"])

        # Regular move
        parsed = parse_move(norm)
        if parsed and parsed["type"] == "move":
            return self._attempt_move(parsed["from"], parsed["to"])

        return self._result(False, "error",
                            f"Did not understand. Please indicate {self.turn}'s move again.")

    def get_state(self) -> GameState:
        """Returns a snapshot of the current game state."""
        return GameState(
            turn=self.turn,
            status=self.status,
            winner=self.winner,
            board_visible=self.board_visible,
            board=deepcopy(self.board),
        )

    def get_legal_moves(self) -> list:
        """
        Returns all legal moves for the current player as a list of dicts:
            {"from": "e2", "to": "e4", "special": None | str}
        Useful for the UI to validate or hint moves.
        """
        if self.status in ("waiting", "checkmate", "stalemate", "forfeit"):
            return []
        raw = get_all_legal_moves(self.board, self.turn,
                                  self.castling_rights, self.en_passant_target)
        return [
            {
                "from": coords_to_square(m["from_row"], m["from_col"]),
                "to": coords_to_square(m["row"], m["col"]),
                "special": m["special"],
            }
            for m in raw
        ]

    # ---- Private Helpers ---------------------------------------------------

    def _reset(self):
        self.board = create_initial_board()
        self.turn = WHITE
        self.status = "waiting"
        self.winner = None
        self.board_visible = False
        self.en_passant_target = None
        self.castling_rights = {
            WHITE: {"kingside": True, "queenside": True},
            BLACK: {"kingside": True, "queenside": True},
        }
        self.move_history = []

    def _start_game(self) -> CommandResult:
        self._reset()
        self.status = "active"
        return self._result(True, "start", "Game started. White to move.")

    def _forfeit(self) -> CommandResult:
        if self.status == "waiting":
            return self._result(False, "error", "No game in progress.")
        self.winner = BLACK if self.turn == WHITE else WHITE
        self.status = "forfeit"
        return self._result(True, "forfeit", f"{self.winner} wins by forfeit.")

    def _attempt_castle(self, castle_type: str) -> CommandResult:
        base_row = 7 if self.turn == WHITE else 0
        to_col = 6 if castle_type == "castle_kingside" else 2
        if not is_legal_move(self.board, base_row, 4, base_row, to_col,
                              castle_type, self.castling_rights, self.en_passant_target):
            return self._result(False, "error",
                                f"Invalid move — castling is not available. "
                                f"Please indicate {self.turn}'s move again.")
        return self._execute_move(base_row, 4, base_row, to_col, castle_type, "king")

    def _attempt_move(self, from_sq: str, to_sq: str) -> CommandResult:
        from_coords = square_to_coords(from_sq)
        to_coords = square_to_coords(to_sq)

        if not from_coords or not to_coords:
            return self._result(False, "error",
                                f"Did not understand the squares. "
                                f"Please indicate {self.turn}'s move again.")

        from_r, from_c = from_coords
        to_r, to_c = to_coords
        cell = self.board[from_r][from_c]

        if not cell:
            return self._result(False, "error",
                                f"No piece on {from_sq}. "
                                f"Please indicate {self.turn}'s move again.")
        if cell["color"] != self.turn:
            return self._result(False, "error",
                                f"That piece belongs to {cell['color']}, not {self.turn}. "
                                f"Please indicate {self.turn}'s move again.")

        pseudo = get_pseudo_legal_moves(self.board, from_r, from_c,
                                        self.en_passant_target, self.castling_rights)
        matched = next((m for m in pseudo if m["row"] == to_r and m["col"] == to_c), None)

        if not matched:
            return self._result(False, "error",
                                f"Invalid move for {cell['piece']}. "
                                f"Please indicate {self.turn}'s move again.")

        if not is_legal_move(self.board, from_r, from_c, to_r, to_c,
                             matched["special"], self.castling_rights, self.en_passant_target):
            return self._result(False, "error",
                                f"That move would leave {self.turn}'s king in check. "
                                f"Please indicate {self.turn}'s move again.")

        return self._execute_move(from_r, from_c, to_r, to_c,
                                  matched["special"], cell["piece"])

    def _execute_move(self, from_row, from_col, to_row, to_col,
                      special, piece) -> CommandResult:
        from_sq = coords_to_square(from_row, from_col)
        to_sq = coords_to_square(to_row, to_col)

        result = apply_move(self.board, from_row, from_col, to_row, to_col,
                            special, self.castling_rights)

        self.board = result["board"]
        self.en_passant_target = result["en_passant_target"]
        self.castling_rights = result["castling_rights"]

        move_desc = build_move_description(
            piece, from_sq, to_sq,
            result["captured_piece"], special, result["promotion_occurred"]
        )
        self.move_history.append(move_desc)

        prev_turn = self.turn
        self.turn = BLACK if self.turn == WHITE else WHITE

        legal_moves = get_all_legal_moves(self.board, self.turn,
                                          self.castling_rights, self.en_passant_target)
        now_in_check = is_in_check(self.board, self.turn)

        status_msg = ""
        if not legal_moves:
            if now_in_check:
                self.status = "checkmate"
                self.winner = prev_turn
                status_msg = f" Checkmate — {prev_turn} wins!"
            else:
                self.status = "stalemate"
                self.winner = None
                status_msg = " Stalemate — the game is a draw."
        elif now_in_check:
            self.status = "check"
            status_msg = f" {self.turn}'s king is in check."
        else:
            self.status = "active"

        next_msg = ("" if self.status in ("checkmate", "stalemate")
                    else f" {self.turn} to move.")

        return self._result(True, "move", f"{move_desc}{status_msg}{next_msg}")

    def _result(self, success: bool, type_: str, message: str) -> CommandResult:
        return CommandResult(
            success=success,
            type=type_,
            message=message,
            state=self.get_state(),
        )


# ---------------------------------------------------------------------------
# Quick smoke test (run: python chesslogic.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    game = ChessGame()
    commands = [
        "start game",
        "e2 to e4",
        "e7 to e5",
        "g1 to f3",
        "b8 to c6",
        "reveal board",
        "queen's neighbors",
        "hide board",
        "check status",
        "forfeit",
    ]
    for cmd in commands:
        result = game.handle_command(cmd)
        prefix = "[OK]" if result.success else "[ERR]"
        print(f"{prefix} > {cmd}")
        print(f"       {result.message}")
        print(f"       turn={result.state.turn}  status={result.state.status}")
        print()