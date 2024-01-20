import os, uuid
from PIL import Image
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

from player_routes import current_track
from models import db, User, Song, Album, Rating
from app import app

def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        print(session)
        if "user_id" not in session:
            print("hi")
            flash("please login to continue", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return inner


def save_img(image, image_path, size=(256, 256)):
    with Image.open(image) as img:
        img = img.resize(size, Image.Resampling.LANCZOS)
        img.convert("RGB").save(image_path, "JPEG")


@app.route("/")
@auth_required
def index():
    user = User.query.get(session["user_id"])
    if user.is_admin:
        return redirect(url_for("admin"))
    return render_template("index.html", user=user, current_track=current_track)


@app.route("/admin")
@auth_required
def admin():
    user = User.query.get(session["user_id"])
    return render_template("admin.html", user=user)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()

    if username == "" and password == "":
        flash("username or password cannot be empty", "danger")
        return redirect(url_for("login"))

    if not user:
        flash("user doesnot exist", "danger")
        return redirect(url_for("login"))

    if not user.check_password(password):
        flash("incorrect password", "danger")
        return redirect(url_for("login"))

    session["user_id"] = user.id
    return redirect(url_for("index"))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=["post"])
def register_post():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if username == "" or password == "" or email == "":
        flash("username, email or password cannot be empty", "danger")
        return redirect(url_for("register"))

    if User.query.filter_by(username=username).first():
        flash("username already exists", "danger")
        return redirect(url_for("register"))

    if User.query.filter_by(email=email).first():
        flash("Someone with that email already exists", "danger")
        return redirect(url_for("register"))

    user = User(username=username, email=email, password=password)
    pfp_file = request.files["pfp"]
    if pfp_file:
        pfp_url = os.path.join(
            app.config["UPLOAD_FOLDER"], "accounts", str(uuid.uuid4().hex) + "_pfp.jpg"
        )
        save_img(pfp_file, pfp_url)
        user.pfp_url = pfp_url

    db.session.add(user)
    db.session.commit()

    flash("User successfully registered", "success")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))
