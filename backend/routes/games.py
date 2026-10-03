from flask import Blueprint, request, jsonify
import db

games_bp = Blueprint("games", __name__, url_prefix="/api/games")


@games_bp.get("/family-quiz/<int:user_id>/questions")
def family_quiz_questions(user_id):
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404
    members = db.get_family_members(user_id)
    if not members:
        return jsonify({"error": "no family members registered yet"}), 404
    return jsonify(members)


@games_bp.post("/family-quiz/<int:user_id>/submit")
def submit_family_quiz(user_id):
    return _submit_game_result(user_id, game="family_quiz")


@games_bp.get("/memory-shuffle/<int:user_id>/cards")
def memory_shuffle_cards(user_id):
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404
    members = db.get_family_members(user_id)
    if not members:
        return jsonify({"error": "no family members registered yet"}), 404
    return jsonify(members)


@games_bp.post("/memory-shuffle/<int:user_id>/submit")
def submit_memory_shuffle(user_id):
    return _submit_game_result(user_id, game="memory_shuffle")


def _submit_game_result(user_id, game):
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404
    data = request.get_json(force=True) or {}
    try:
        score = float(data.get("score"))
        accuracy = float(data.get("accuracy"))
        time_taken = float(data.get("time_taken"))
        attempts = int(data.get("attempts"))
    except (TypeError, ValueError):
        return jsonify({"error": "score, accuracy, time_taken, attempts are required numbers"}), 400

    level_reached = data.get("level_reached")
    performance_label = data.get("performance_label")

    entry = db.record_game_result(
        user_id, game, score, accuracy, time_taken, attempts,
        level_reached=level_reached, performance_label=performance_label,
    )
    return jsonify(entry), 201