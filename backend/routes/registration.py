from flask import Blueprint, request, jsonify
import db
import storage

registration_bp = Blueprint("registration", __name__, url_prefix="/api/registration")


def _public_user(user):
    return {k: v for k, v in user.items() if k != "password_hash"}


@registration_bp.get("/<int:user_id>")
def get_user(user_id):
    """
    Backs profile.html's patient info + caregiver info sections.
    Account creation itself now lives at POST /api/auth/register.
    """
    user = db.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify({**_public_user(user), "medicines": db.get_medicines(user_id)})

@registration_bp.patch("/<int:user_id>/language")
def update_language(user_id):
    """Lets a user change their preferred UI language from the Profile page."""
    data = request.get_json(force=True) or {}
    language = data.get("language")
    if not language:
        return jsonify({"error": "language is required"}), 400
    user = db.update_user_language(user_id, language)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify(_public_user(user))

@registration_bp.get("/")
def list_users():
    return jsonify([_public_user(u) for u in db.list_users()])


# ---------------- Family members ----------------

@registration_bp.get("/<int:user_id>/family-members")
def get_family_members(user_id):
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404
    return jsonify(db.get_family_members(user_id))


@registration_bp.post("/<int:user_id>/family-members")
def add_family_members(user_id):
    """
    Matches form.html's "Meet Your Family" form: repeatable fieldsets
    submitted together as member_name[], member_photo[], member_relation[]
    (multipart/form-data, one POST covers every family member added on
    that page, not just one).

    Also still accepts a single JSON member {name, relation, photo_url}
    for callers that aren't the batch form.
    """
    if not db.get_user(user_id):
        return jsonify({"error": "user not found"}), 404

    if "member_name[]" in request.form:
        names = request.form.getlist("member_name[]")
        relations = request.form.getlist("member_relation[]")
        photos = request.files.getlist("member_photo[]")

        if not (len(names) == len(relations) == len(photos)):
            return jsonify({
                "error": "member_name[], member_relation[], and member_photo[] must all have the same count"
            }), 400

        created = []
        for name, relation, file in zip(names, relations, photos):
            if not name or not relation:
                return jsonify({"error": "every family member needs a name and relation"}), 400
            photo_url = storage.upload_file(file.read(), file.filename, file.content_type) if file.filename else None
            created.append(db.add_family_member(user_id, name, relation, photo_url))

        return jsonify(created), 201

    if "photo" in request.files:
        name = request.form.get("name")
        relation = request.form.get("relation")
        file = request.files["photo"]
        photo_url = storage.upload_file(file.read(), file.filename, file.content_type) if file.filename else None
        if not name or not relation:
            return jsonify({"error": "name and relation are required"}), 400
        entry = db.add_family_member(user_id, name, relation, photo_url)
        return jsonify(entry), 201

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    relation = data.get("relation")
    photo_url = data.get("photo_url")
    if not name or not relation:
        return jsonify({"error": "name and relation are required"}), 400
    entry = db.add_family_member(user_id, name, relation, photo_url)
    return jsonify(entry), 201