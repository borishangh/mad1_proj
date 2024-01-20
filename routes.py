from flask import flask, render_template, redirect, request, url_for, flash

from models import db, User, Album, Song, Rating
from app import app


@app.route("/")
def index():
    return render_template("index.html")
