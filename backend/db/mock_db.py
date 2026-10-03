"""
mock_db.py
----------
TEMPORARY in-memory "database". Data resets every time the server
restarts — that's fine, it's only here so the backend, frontend, and
AI/ML integration can all be built and tested before Supabase exists.

Every function here matches, 1-to-1, a function in supabase_db.py.
db/__init__.py picks whichever module to use based on config.USE_MOCK_DB.
Routes never import this file directly.
"""

import itertools
from datetime import datetime

_id_counter = itertools.count(1)


def _next_id():
    return next(_id_counter)


USERS = {}
MEDICINES = {}
FAMILY_MEMBERS = {}
MEMORIES = {}
GAME_SCORES = {}
REMINDERS = {}


# ---------------- Users ----------------

def create_user(username, name, email, password_hash, phone=None, address=None,
                 caregiver_name=None, caregiver_phone=None, birthday=None,
                 language=None, medicines=None):
    user_id = _next_id()
    USERS[user_id] = {
        "id": user_id,
        "username": username,
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "phone": phone,
        "address": address,
        "caregiver_name": caregiver_name,
        "caregiver_phone": caregiver_phone,
        "birthday": birthday,
        "language": language or "en",
        "created_at": datetime.utcnow().isoformat(),
    }
    MEDICINES.setdefault(user_id, [])
    FAMILY_MEMBERS.setdefault(user_id, [])
    MEMORIES.setdefault(user_id, [])
    GAME_SCORES.setdefault(user_id, [])
    REMINDERS.setdefault(user_id, [])

    if medicines:
        for m in medicines:
            add_medicine(user_id, m.get("name"), m.get("time"), m.get("dosage"))

    return USERS[user_id]


def get_user(user_id):
    return USERS.get(user_id)


def get_user_by_email(email):
    for user in USERS.values():
        if user["email"] == email:
            return user
    return None


def get_user_by_username(username):
    for user in USERS.values():
        if user.get("username") == username:
            return user
    return None


def update_user_language(user_id, language):
    user = USERS.get(user_id)
    if not user:
        return None
    user["language"] = language
    return user


def list_users():
    return list(USERS.values())


# ---------------- Medicines ----------------

def add_medicine(user_id, name, time=None, dosage=None):
    entry = {"id": _next_id(), "user_id": user_id, "name": name, "time": time, "dosage": dosage}
    MEDICINES.setdefault(user_id, []).append(entry)
    return entry


def get_medicines(user_id):
    return MEDICINES.get(user_id, [])


# ---------------- Reminders ----------------

def add_reminder(user_id, text, time, note=None):
    entry = {"id": _next_id(), "user_id": user_id, "text": text, "time": time, "note": note, "done": False}
    REMINDERS.setdefault(user_id, []).append(entry)
    return entry


def get_reminders(user_id):
    return REMINDERS.get(user_id, [])


def mark_reminder_done(user_id, reminder_id):
    for r in REMINDERS.get(user_id, []):
        if r["id"] == reminder_id:
            r["done"] = True
            return r
    return None


# ---------------- Family members ----------------

def add_family_member(user_id, name, relation, photo_url=None):
    entry = {"id": _next_id(), "user_id": user_id, "name": name, "relation": relation, "photo_url": photo_url}
    FAMILY_MEMBERS.setdefault(user_id, []).append(entry)
    return entry


def get_family_members(user_id):
    return FAMILY_MEMBERS.get(user_id, [])


# ---------------- Memories / photos ----------------

def add_memory(user_id, photo_url, caption=None):
    entry = {"id": _next_id(), "user_id": user_id, "photo_url": photo_url, "caption": caption}
    MEMORIES.setdefault(user_id, []).append(entry)
    return entry


def get_memories(user_id):
    return MEMORIES.get(user_id, [])


# ---------------- Game scores ----------------

def record_game_result(user_id, game, score, accuracy, time_taken, attempts,
                        level_reached=None, performance_label=None):
    entry = {
        "id": _next_id(),
        "user_id": user_id,
        "game": game,
        "score": score,
        "accuracy": accuracy,
        "time_taken": time_taken,
        "attempts": attempts,
        "level_reached": level_reached,
        "performance_label": performance_label,
        "created_at": datetime.utcnow().isoformat(),
    }
    GAME_SCORES.setdefault(user_id, []).append(entry)
    return entry


def get_game_scores(user_id, game=None):
    scores = GAME_SCORES.get(user_id, [])
    if game:
        scores = [s for s in scores if s["game"] == game]
    return sorted(scores, key=lambda s: s["created_at"], reverse=True)


def get_performance_summary(user_id):
    scores = GAME_SCORES.get(user_id, [])
    if not scores:
        return {
            "games_played": 0,
            "avg_score": 0,
            "avg_accuracy": 0,
            "avg_time_taken": 0,
            "latest_level_reached": None,
            "latest_performance_label": None,
        }
    games_played = len(scores)
    avg_score = sum(s["score"] for s in scores) / games_played
    avg_accuracy = sum(s["accuracy"] for s in scores) / games_played
    avg_time_taken = sum(s["time_taken"] for s in scores) / games_played

    sorted_scores = sorted(scores, key=lambda s: s["created_at"], reverse=True)
    latest_with_level = next((s for s in sorted_scores if s.get("level_reached") is not None), None)

    return {
        "games_played": games_played,
        "avg_score": round(avg_score, 2),
        "avg_accuracy": round(avg_accuracy, 2),
        "avg_time_taken": round(avg_time_taken, 2),
        "latest_level_reached": latest_with_level["level_reached"] if latest_with_level else None,
        "latest_performance_label": latest_with_level["performance_label"] if latest_with_level else None,
    }