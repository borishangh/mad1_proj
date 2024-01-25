import os, uuid
from PIL import Image
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

from player_routes import current_track, stop_music
from models import db, User, Song, Album, Rating, Genre
from app import app

from routes import auth_required


@app.route("/admin")
@auth_required
def admin():
    user = User.query.get(session["user_id"])
    genres = Genre.query.all()
    stats = {
        "total_users": db.session.query(User).count() - 1,
        "total_songs": db.session.query(Song).count(),
        "total_plays": db.session.query(db.func.sum(Song.plays)).scalar() or 0,
    }
    genre_info = dict(
        db.session.query(Genre.name, db.func.count(Song.id))
        .outerjoin(Song, Genre.id == Song.genre_id)
        .group_by(Genre.name)
        .all()
    )
    users = User.query.all()
    songs = Song.query.all()
    albums = Album.query.all()

    return render_template(
        "admin.html",
        user=user,
        users=users,
        songs=songs,
        albums=albums,
        genre_info=genre_info,
        stats=stats,
    )


@app.route("/blacklist_user/<int:user_id>")
def blacklist_user(user_id):
    user = User.query.get(user_id)
    user.is_blacklisted = True
    db.session.commit()
    return redirect(request.referrer)


@app.route("/whitelist_user/<int:user_id>")
def whitelist_user(user_id):
    user = User.query.get(user_id)
    user.is_blacklisted = False
    db.session.commit()
    return redirect(request.referrer)


@app.route('/remove_user/<int:user_id>')
def remove_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/flag_song/<int:song_id>')
def flag_song(song_id):
    song = Song.query.get(song_id)
    song.is_flagged = not song.is_flagged
    db.session.commit()
    return redirect(request.referrer)

@app.route('/flag_album/<int:album_id>')
def flag_album(album_id):
    album = Album.query.get(album_id)
    album.is_flagged = not album.is_flagged
    db.session.commit()
    return redirect(request.referrer)