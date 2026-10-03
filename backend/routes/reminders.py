from flask import Blueprint, request, jsonify
import db

reminders_bp = Blueprint("reminders", __name__, url_prefix="/api/reminders")


@reminders_bp.get("/<int:user_id>")
def get_reminders(user_id):
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404
    return jsonify({
        "medicines": db.get_medicines(user_id),
        "reminders": db.get_reminders(user_id),
    })


@reminders_bp.post("/<int:user_id>")
def add_reminder(user_id):
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404
    data = request.get_json(force=True) or {}
    text = data.get("text")
    time = data.get("time")
    note = data.get("note")
    if not text or not time:
        return jsonify({"error": "text and time are required"}), 400
    entry = db.add_reminder(user_id, text, time, note=note)
    return jsonify(entry), 201


@reminders_bp.post("/<int:user_id>/medicines")
def add_medicine(user_id):
    """
    Lets a medicine be added to an existing account after registration —
    previously the only way to get a medicine on file was the
    registration form itself.
    """
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404
    data = request.get_json(force=True) or {}
    name = data.get("name")
    dosage = data.get("dosage")
    time = data.get("time")
    if not name:
        return jsonify({"error": "medicine name is required"}), 400
    entry = db.add_medicine(user_id, name, time=time, dosage=dosage)
    return jsonify(entry), 201


@reminders_bp.patch("/<int:user_id>/<int:reminder_id>/done")
def complete_reminder(user_id, reminder_id):
    entry = db.mark_reminder_done(user_id, reminder_id)
    if not entry:
        return jsonify({"error": "reminder not found"}), 404
    return jsonify(entry)