import os, uuid
from PIL import Image
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

from player_routes import current_track, stop_music
from models import db, User, Song, Album, Rating, Playlist
from app import app
from routes import auth_required, save_img


@app.route("/playlist/<int:playlist_id>")
@auth_required
def playlist_detail(playlist_id):
    user = User.query.get(session["user_id"])
    playlist = Playlist.query.get_or_404(playlist_id)
    songs = playlist.songs.all()

    return render_template(
        "playlist.html",
        playlist=playlist,
        songs=songs,
        user=user,
        current_track=current_track,
    )


@app.route("/create-playlist", methods=["POST"])
@auth_required
def create_playlist():
    user = User.query.get(session["user_id"])
    playlist_name = request.form.get("playlist-name")

    if not playlist_name:
        flash("Playlist name is required.", "error")
        return redirect(request.referrer)

    cover_file = request.files["playlist-cover"]
    if cover_file:
        playlist_cover_url = os.path.join(
            "playlists",
            str(uuid.uuid4().hex) + "_playlist.jpg",
        )
        save_img(cover_file, os.path.join("static", playlist_cover_url))

        new_playlist = Playlist(
            name=playlist_name,
            cover_url=playlist_cover_url,
            creator_id=session["user_id"],
        )
    else:
        new_playlist = Playlist(name=playlist_name, creator_id=session["user_id"])

    db.session.add(new_playlist)
    db.session.commit()

    return redirect(request.referrer)


@app.route("/add_to_playlist", methods=["POST"])
def add_to_playlist():
    selected = request.form.get("selected").split(" ")
    song_id = selected[0]
    playlist_id = selected[1]

    if song_id and playlist_id:
        song = Song.query.get(song_id)
        playlist = Playlist.query.get(playlist_id)

        if not playlist.songs or song not in playlist.songs:
            playlist.songs.append(song)
        db.session.commit()

    return redirect(request.referrer)
