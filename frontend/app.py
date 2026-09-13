import os
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    flash,
    session,
    send_from_directory
)
from dotenv import load_dotenv
import requests
from functools import wraps
from datetime import datetime
from translations import t, LANGUAGE_NAMES


# =========================================================
# LOGIN REQUIRED DECORATOR
# =========================================================

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "error")
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return wrapper


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

BACKEND_URL = "http://127.0.0.1:5000/api"

app = Flask(__name__)
app.secret_key = "dev-secret-change-later"
MEMORYSHUFFLE_DIR = os.path.join(
    app.root_path,
    "..",
    "web-game",
    "games",
    "MemoryShuffle"
)

FAMILYMEMORY_DIR = os.path.join(
    app.root_path,
    "..",
    "web-game",
    "games",
    "FamilyMemory"
)



# =========================================================
# TRANSLATIONS
# =========================================================

@app.context_processor
def inject_translation():
    lang = session.get("language", "en")

    return dict(
        t=lambda key, **kwargs: t(key, lang, **kwargs),
        lang=lang,
        LANGUAGE_NAMES=LANGUAGE_NAMES
    )


# =========================================================
# INDEX
# =========================================================

@app.route("/")
def index():
    return redirect(url_for("login"))


# =========================================================
# FORM
# =========================================================

@app.route("/form", methods=["GET", "POST"])
@login_required
def form():

    if request.method == "POST":

        user_id = session.get("user_id")

        if not user_id:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))

        names = request.form.getlist("member_name[]")
        relations = request.form.getlist("member_relation[]")
        photos = request.files.getlist("member_photo[]")

        data = {
            "member_name[]": names,
            "member_relation[]": relations,
        }

        files = [
            (
                "member_photo[]",
                (f.filename, f.read(), f.mimetype)
            )
            for f in photos
            if f.filename
        ]

        response = requests.post(
            f"{BACKEND_URL}/registration/{user_id}/family-members",
            data=data,
            files=files,
        )

        if response.status_code == 201:

            flash(
                "Family members saved!",
                "success"
            )

            return redirect(url_for("home"))

        else:

            flash(
                response.json().get(
                    "error",
                    "Could not save family members"
                ),
                "error"
            )

            return redirect(url_for("form"))

    return render_template("form.html")


# =========================================================
# HOME
# =========================================================

@app.route("/home")
@login_required
def home():

    user_id = session.get("user_id")

    user_response = requests.get(
        f"{BACKEND_URL}/registration/{user_id}"
    )

    reminders_response = requests.get(
        f"{BACKEND_URL}/reminders/{user_id}"
    )

    user = (
        user_response.json()
        if user_response.status_code == 200
        else {}
    )

    reminders_data = (
        reminders_response.json()
        if reminders_response.status_code == 200
        else {
            "medicines": [],
            "reminders": []
        }
    )

    now = datetime.now()

    now_minutes = (
        now.hour * 60
        + now.minute
    )

    all_items = []

    # Medicines
    for m in reminders_data.get("medicines", []):

        all_items.append({
            "text": m["name"],
            "time": m["time"]
        })

    # Reminders
    for r in reminders_data.get("reminders", []):

        if not r.get("done"):

            all_items.append({
                "text": r["text"],
                "time": r["time"]
            })

    upcoming = None
    best_diff = None

    for item in all_items:

        try:

            h, mi = map(
                int,
                item["time"].split(":")
            )

        except (ValueError, AttributeError):

            continue

        item_minutes = (
            h * 60
            + mi
        )

        diff = (
            item_minutes
            - now_minutes
        )

        if diff < 0:

            diff += 24 * 60

        if (
            best_diff is None
            or diff < best_diff
        ):

            best_diff = diff
            upcoming = item

    return render_template(
        "home.html",
        user=user,
        upcoming=upcoming
    )


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        medicine_names = request.form.getlist(
            "medicine_name[]"
        )

        medicine_times = request.form.getlist(
            "medicine_time[]"
        )

        medicines = [
            {
                "name": name,
                "time": time
            }

            for name, time in zip(
                medicine_names,
                medicine_times
            )

            if name and time
        ]

        data = {

            "name": request.form.get("name"),

            "email": request.form.get("email"),

            "phone": request.form.get("phone"),

            "address": request.form.get("address"),

            "birthday": request.form.get("birthday"),

            "language": request.form.get("language"),

            "caregiver_name": request.form.get("c-name"),

            "caregiver_phone": request.form.get("c-phone"),

            "password": request.form.get("password"),

            "medicines": medicines,

        }

        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=data
        )

        if response.status_code == 201:

            user = response.json()

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            session["language"] = user.get(
                "language",
                "en"
            )

            return redirect(
                url_for("form")
            )

        else:

            flash(
                response.json().get(
                    "error",
                    "Registration failed"
                ),
                "error"
            )

            return redirect(
                url_for("register")
            )

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")

        password = request.form.get("password")

        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": email,
                "password": password,
            }
        )

        if response.status_code == 200:

            user = response.json()

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            session["language"] = user.get(
                "language",
                "en"
            )

            return redirect(
                url_for("home")
            )

        else:

            flash(
                response.json().get(
                    "error",
                    "Login failed"
                ),
                "error"
            )

            return redirect(
                url_for("login")
            )

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
@login_required
def profile():

    user_id = session.get("user_id")

    user_response = requests.get(
        f"{BACKEND_URL}/registration/{user_id}"
    )

    family_response = requests.get(
        f"{BACKEND_URL}/registration/{user_id}/family-members"
    )

    user = (
        user_response.json()
        if user_response.status_code == 200
        else {}
    )

    family_members = (
        family_response.json()
        if family_response.status_code == 200
        else []
    )

    return render_template(
        "profile.html",
        user=user,
        family_members=family_members
    )

@app.route("/set-language", methods=["POST"])
@login_required
def set_language():
    user_id = session.get("user_id")
    language = request.form.get("language")

    response = requests.patch(f"{BACKEND_URL}/registration/{user_id}/language", json={"language": language})

    if response.status_code == 200:
        session["language"] = language
        flash("Language updated!", "success")
    else:
        flash("Could not update language.", "error")

    return redirect(url_for("profile"))
# =========================================================
# PHOTOS
# =========================================================

@app.route("/photo", methods=["GET", "POST"])
@login_required
def photo():

    user_id = session.get("user_id")

    if request.method == "POST":

        file = request.files.get("photo")

        caption = request.form.get("caption")

        if not file or file.filename == "":

            flash(
                "Please choose a photo to upload.",
                "error"
            )

            return redirect(
                url_for("photo")
            )

        files = {
            "photo": (
                file.filename,
                file.read(),
                file.mimetype
            )
        }

        data = {
            "caption": caption
        }

        response = requests.post(
            f"{BACKEND_URL}/photos/{user_id}",
            data=data,
            files=files
        )

        print(
            "BACKEND RESPONSE:",
            response.status_code,
            repr(response.text[:300])
        )

        if response.status_code == 201:

            flash(
                "Photo saved!",
                "success"
            )

        else:

            try:

                error_message = response.json().get(
                    "error",
                    "Could not save photo"
                )

            except ValueError:

                error_message = (
                    "Could not save photo "
                    f"(server error {response.status_code})"
                )

            flash(
                error_message,
                "error"
            )

        return redirect(
            url_for("photo")
        )

    photos_response = requests.get(
        f"{BACKEND_URL}/photos/{user_id}"
    )

    photos = (
        photos_response.json()
        if photos_response.status_code == 200
        else []
    )

    return render_template(
        "photo.html",
        photos=photos
    )


# =========================================================
# REMINDERS
# =========================================================

@app.route("/reminders", methods=["GET", "POST"])
@login_required
def reminders():

    user_id = session.get("user_id")

    if request.method == "POST":

        text = request.form.get("text")

        time = request.form.get("time")

        response = requests.post(
            f"{BACKEND_URL}/reminders/{user_id}",
            json={
                "text": text,
                "time": time
            }
        )

        if response.status_code == 201:

            flash(
                "Reminder added!",
                "success"
            )

        else:

            try:

                error_message = response.json().get(
                    "error",
                    "Could not add reminder"
                )

            except ValueError:

                error_message = (
                    "Could not add reminder "
                    f"(server error {response.status_code})"
                )

            flash(
                error_message,
                "error"
            )

        return redirect(
            url_for("reminders")
        )

    reminders_response = requests.get(
        f"{BACKEND_URL}/reminders/{user_id}"
    )

    data = (
        reminders_response.json()
        if reminders_response.status_code == 200
        else {
            "medicines": [],
            "reminders": []
        }
    )

    return render_template(
        "reminders.html",
        medicines=data.get(
            "medicines",
            []
        ),
        reminders=data.get(
            "reminders",
            []
        )
    )


# =========================================================
# COMPLETE REMINDER
# =========================================================

@app.route(
    "/reminders/<int:reminder_id>/done"
)
@login_required
def complete_reminder(reminder_id):

    user_id = session.get("user_id")

    requests.patch(
        f"{BACKEND_URL}/reminders/"
        f"{user_id}/{reminder_id}/done"
    )

    return redirect(
        url_for("reminders")
    )


# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
@login_required
def history():

    user_id = session.get("user_id")

    response = requests.get(
        f"{BACKEND_URL}/dashboard/"
        f"{user_id}/history"
    )

    activities = (
        response.json()
        if response.status_code == 200
        else []
    )

    return render_template(
        "history.html",
        activities=activities
    )


# =========================================================
# GAMES PAGE
# =========================================================

@app.route("/games")
@login_required
def games():

    return render_template(
        "games.html"
    )


# =========================================================
# UNITY GAME 1
# MEMORY SHUFFLE
# =========================================================

@app.route("/memoryshuffle/")
@login_required
def memoryshuffle():

    return send_from_directory(
        MEMORYSHUFFLE_DIR,
        "index.html"
    )

@app.route(
    "/memoryshuffle/<path:path>"
)
@login_required
def memoryshuffle_files(path):

    return send_from_directory(
        MEMORYSHUFFLE_DIR,
        path
    )


# =========================================================
# UNITY GAME 2
# FAMILY MEMORY
# =========================================================

@app.route("/familymemory/")
@login_required
def familymemory():

    return send_from_directory(
        FAMILYMEMORY_DIR,
        "index.html"
    )


@app.route(
    "/familymemory/<path:path>"
)
@login_required
def familymemory_files(path):

    return send_from_directory(
        FAMILYMEMORY_DIR,
        path
    )


# =========================================================
# QUIZ
# KEEPING THIS FOR NOW
# =========================================================

@app.route("/quiz")
@login_required
def quiz():

    return render_template(
        "quiz.html"
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )