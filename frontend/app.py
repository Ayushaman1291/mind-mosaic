import os
from flask import Flask,render_template,redirect,request,url_for,flash
from dotenv import load_dotenv

load_dotenv()

app=Flask(__name__)

@app.route("/")
def index():
    # return render_template("home.html")
    return redirect(url_for("login"))


@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        return redirect(url_for("form"))
    return render_template("register.html")


# @app.route("/register/family", methods=["GET", "POST"])
# def family_setup():
#     if request.method == "POST":
#         names = request.form.getlist("member_name[]")
#         photos = request.files.getlist("member_photo[]")

#         for name, photo in zip(names, photos):
#             if not name or not photo or photo.filename == "":
#                 continue

#             extension = photo.filename.rsplit(".", 1)[-1].lower()

#             if extension not in ALLOWED_EXTENSIONS:
#                 flash(f"{name}'s photo must be JPG, PNG, or WEBP.", "error")
#                 return redirect(url_for("family_setup"))

#             filename = f"{uuid4().hex}_{secure_filename(photo.filename)}"
#             photo.save(UPLOAD_FOLDER / filename)

#             # Later: save name + filename in the database for this user.

#         flash("Your family photos have been saved.", "success")
#         return redirect(url_for("home"))

#     return render_template("family_setup.html")



@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    flash("you have been logged out","success")
    return redirect(url_for("home"))

@app.route("/profile",methods=["GET","POST"])
def profile():
    return render_template("profile.html")

@app.route("/photo")
def photo():
    return render_template("photo.html")

@app.route("/puzzle")
def puzzle():
    return render_template("puzzle.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


if __name__=="__main__":
    app.run(debug=True)