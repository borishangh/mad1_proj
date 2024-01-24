import os, uuid
from PIL import Image
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

from player_routes import current_track, stop_music
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


from sqlalchemy import func


@app.route("/")
@auth_required
def index():
    user = User.query.get(session["user_id"])
    if user.is_admin:
        return redirect(url_for("admin"))

    top_songs = Song.query.order_by(Song.plays.desc()).limit(12).all()
    top_albums = (
        db.session.query(Album, func.sum(Song.plays).label("total_plays"))
        .join(Song, Album.id == Song.album_id, isouter=True)
        .group_by(Album)
        .order_by(func.sum(Song.plays).desc())
        .limit(12)
        .all()
    )

    featured = {"songs": top_songs, "albums": top_albums}
    return render_template(
        "index.html", user=user, current_track=current_track, featured=featured
    )


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
        pfp_url = os.path.join("accounts", str(uuid.uuid4().hex) + "_pfp.jpg")
        save_img(pfp_file, os.path.join("static", pfp_url))
        user.pfp_url = pfp_url

    db.session.add(user)
    db.session.commit()

    flash("User successfully registered", "success")
    return redirect(url_for("index"))


@app.route("/logout")
@auth_required
def logout():
    stop_music()
    session.pop("user_id", None)
    return redirect(url_for("index"))


@app.route("/profile")
@auth_required
def profile():
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user, current_track=current_track)


@app.route("/profile", methods=["POST"])
@auth_required
def profile_post():
    user = User.query.get(session["user_id"])
    username = request.form.get("username")
    email = request.form.get("email")

    cpassword = request.form.get("cpassword")
    password = request.form.get("password")

    if username == "" or email == "":
        flash("Username or email cannot be empty", "danger")
        return redirect(url_for("profile"))

    if not user.check_password(cpassword) and cpassword != "":
        flash("Incorrect password entered.", "danger")
        return redirect(url_for("profile"))

    pfp_file = request.files["pfp"]

    if pfp_file:
        pfp_url = os.path.join(
            "accounts",
            str(uuid.uuid4().hex) + "_pfp.jpg",
        )
        user.pfp_url = pfp_url
        save_img(pfp_file, os.path.join("static", pfp_url))

    user.username = username
    user.email = email
    user.password = password

    db.session.commit()
    flash("Profile updated successfully", "success")
    return redirect(url_for("index"))
