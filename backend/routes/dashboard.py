from flask import Blueprint, request, jsonify
import db

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("/<int:user_id>/summary")
def performance_summary(user_id):
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404
    return jsonify(db.get_performance_summary(user_id))


@dashboard_bp.get("/<int:user_id>/history")
def activity_history(user_id):
    """Full activity/score history, optionally filtered by ?game=family_quiz"""
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404
    game = request.args.get("game")
    return jsonify(db.get_game_scores(user_id, game=game))
