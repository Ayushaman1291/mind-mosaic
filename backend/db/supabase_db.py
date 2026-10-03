"""
supabase_db.py
---------------
Real database backend, talking to Supabase (Postgres).

Every function here matches, 1-to-1, a function in mock_db.py.
db/__init__.py picks whichever module to use based on config.USE_MOCK_DB.
Routes never import this file directly — so when this file is switched
in, no route code changes.

Requires the tables from schema.sql to already exist in your Supabase
project, and SUPABASE_URL / SUPABASE_KEY set in .env.
"""

from supabase_client import supabase


# ---------------- Users ----------------

def create_user(username, name, email, password_hash, phone=None, address=None,
                 caregiver_name=None, caregiver_phone=None, birthday=None,
                 language=None, medicines=None):
    res = supabase.table("users").insert({
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
    }).execute()
    user = res.data[0]

    if medicines:
        for m in medicines:
            add_medicine(user["id"], m.get("name"), m.get("time"), m.get("dosage"))

    return user


def get_user(user_id):
    res = supabase.table("users").select("*").eq("id", user_id).execute()
    return res.data[0] if res.data else None


def get_user_by_email(email):
    res = supabase.table("users").select("*").eq("email", email).execute()
    return res.data[0] if res.data else None


def get_user_by_username(username):
    res = supabase.table("users").select("*").eq("username", username).execute()
    return res.data[0] if res.data else None


def update_user_language(user_id, language):
    res = supabase.table("users").update({"language": language}).eq("id", user_id).execute()
    return res.data[0] if res.data else None


def list_users():
    res = supabase.table("users").select("*").execute()
    return res.data


# ---------------- Medicines ----------------

def add_medicine(user_id, name, time=None, dosage=None):
    res = supabase.table("medicines").insert({"user_id": user_id, "name": name, "time": time, "dosage": dosage}).execute()
    return res.data[0]


def get_medicines(user_id):
    res = supabase.table("medicines").select("*").eq("user_id", user_id).execute()
    return res.data


# ---------------- Reminders ----------------

def add_reminder(user_id, text, time, note=None):
    res = supabase.table("reminders").insert(
        {"user_id": user_id, "text": text, "time": time, "note": note, "done": False}
    ).execute()
    return res.data[0]


def get_reminders(user_id):
    res = supabase.table("reminders").select("*").eq("user_id", user_id).execute()
    return res.data


def mark_reminder_done(user_id, reminder_id):
    res = supabase.table("reminders").update({"done": True}).eq("id", reminder_id).eq("user_id", user_id).execute()
    return res.data[0] if res.data else None


# ---------------- Family members ----------------

def add_family_member(user_id, name, relation, photo_url=None):
    res = supabase.table("family_members").insert(
        {"user_id": user_id, "name": name, "relation": relation, "photo_url": photo_url}
    ).execute()
    return res.data[0]


def get_family_members(user_id):
    res = supabase.table("family_members").select("*").eq("user_id", user_id).execute()
    return res.data


# ---------------- Memories / photos ----------------

def add_memory(user_id, photo_url, caption=None):
    res = supabase.table("memories").insert(
        {"user_id": user_id, "photo_url": photo_url, "caption": caption}
    ).execute()
    return res.data[0]


def get_memories(user_id):
    res = supabase.table("memories").select("*").eq("user_id", user_id).execute()
    return res.data


# ---------------- Game scores ----------------

def record_game_result(user_id, game, score, accuracy, time_taken, attempts,
                        level_reached=None, performance_label=None):
    res = supabase.table("game_scores").insert({
        "user_id": user_id,
        "game": game,
        "score": score,
        "accuracy": accuracy,
        "time_taken": time_taken,
        "attempts": attempts,
        "level_reached": level_reached,
        "performance_label": performance_label,
    }).execute()
    return res.data[0]


def get_game_scores(user_id, game=None):
    query = supabase.table("game_scores").select("*").eq("user_id", user_id)
    if game:
        query = query.eq("game", game)
    res = query.order("created_at", desc=True).execute()
    return res.data


def get_performance_summary(user_id):
    """
    Matches the architecture diagram's Performance Metrics box:
    Progress, Accuracy, Scores, Time.
    """
    res = supabase.table("game_scores").select("*").eq("user_id", user_id).execute()
    scores = res.data
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