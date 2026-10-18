"""
Flask backend for the Myanmar Checkers AI Visualizer.

The server is stateless: the browser keeps the list of moves played so far
(each move is its path of [row, col] squares) and sends it with every
request. The server replays it with the engine, which validates every move,
so the app works with several gunicorn workers and survives restarts.
"""

import os

from flask import Flask, jsonify, render_template, request

from agent import make_agent
from checkers import CheckersGame, PLAYER_NAMES

app = Flask(__name__)

DIFFICULTIES = {
    "easy": "Easy — Random Agent",
    "medium": "Medium — Heuristic Agent",
    "hard": "Hard — Minimax + Alpha-Beta",
}
MAX_HISTORY = 1000


class BadRequest(Exception):
    pass


def replay(history):
    """Rebuild a game from a list of move paths, validating each move."""
    if not isinstance(history, list) or len(history) > MAX_HISTORY:
        raise BadRequest("Invalid move history")
    game = CheckersGame()
    for i, path in enumerate(history):
        if game.is_game_over():
            raise BadRequest(f"Move {i + 1} was played after the game ended")
        move = game.find_move(path) if isinstance(path, list) else None
        if move is None:
            raise BadRequest(f"Move {i + 1} in history is not legal")
        game.make_move(move)
    return game


def state_response(game, history, **extra):
    data = game.to_dict()
    data["history"] = history
    data["moves"] = [entry[0].to_dict() for entry in game.history]
    data["player_names"] = {str(k): v for k, v in PLAYER_NAMES.items()}
    men1, kings1 = game.count_pieces(1)
    men2, kings2 = game.count_pieces(-1)
    data["counts"] = {
        "1": {"men": men1, "kings": kings1},
        "-1": {"men": men2, "kings": kings2},
    }
    data.update(extra)
    return jsonify(data)


def read_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BadRequest("Expected a JSON object")
    return data


@app.errorhandler(BadRequest)
def handle_bad_request(err):
    return jsonify({"error": str(err)}), 400


@app.route("/")
def index():
    return render_template("index.html", difficulties=DIFFICULTIES)


@app.route("/api/state", methods=["POST"])
def api_state():
    """Return the position after the given history (used for new game / undo)."""
    data = read_json()
    history = data.get("history", [])
    game = replay(history)
    return state_response(game, history)


@app.route("/api/move", methods=["POST"])
def api_move():
    """Apply the human's move."""
    data = read_json()
    history = data.get("history", [])
    game = replay(history)
    if game.is_game_over():
        raise BadRequest("The game is already over")
    move = game.find_move(data.get("move") or [])
    if move is None:
        raise BadRequest("Illegal move")
    game.make_move(move)
    history = history + [[list(sq) for sq in move.path]]
    return state_response(game, history, played=move.to_dict())


@app.route("/api/ai_move", methods=["POST"])
def api_ai_move():
    """Let the selected AI agent play one move."""
    data = read_json()
    difficulty = str(data.get("difficulty", "hard")).lower()
    if difficulty not in DIFFICULTIES:
        raise BadRequest("Unknown difficulty")
    history = data.get("history", [])
    game = replay(history)
    if game.is_game_over():
        raise BadRequest("The game is already over")

    agent = make_agent(difficulty)
    move = agent.get_move(game)
    game.make_move(move)
    history = history + [[list(sq) for sq in move.path]]
    return state_response(game, history, played=move.to_dict(), ai_stats=agent.stats)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
