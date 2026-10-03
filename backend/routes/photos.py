from flask import Blueprint, request, jsonify
import db
import storage

photos_bp = Blueprint("photos", __name__, url_prefix="/api/photos")


@photos_bp.get("/<int:user_id>")
def get_memories(user_id):
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404
    return jsonify(db.get_memories(user_id))


@photos_bp.post("/<int:user_id>")
def add_memory(user_id):
    """
    1. multipart/form-data with a "photo" file field (+ optional
       "person_name") — real file upload, saved via storage.upload_file().
    2. application/json with {"photo_url": "...", "person_name": "..."} —
       when a photo is already hosted elsewhere.
    """
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404

    if "photo" in request.files:
        file = request.files["photo"]
        if file.filename == "":
            return jsonify({"error": "no file selected"}), 400
        # FIXED: photo.html's field is "person_name", not "caption".
        # Still accepts "caption" too, for anything else still using it.
        caption = request.form.get("person_name") or request.form.get("caption")
        photo_url = storage.upload_file(file.read(), file.filename, file.content_type)
    else:
        data = request.get_json(silent=True) or {}
        photo_url = data.get("photo_url")
        caption = data.get("person_name") or data.get("caption")
        if not photo_url:
            return jsonify({"error": "provide either a 'photo' file or a 'photo_url'"}), 400

    entry = db.add_memory(user_id, photo_url, caption)
    return jsonify(entry), 201