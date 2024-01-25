import os
import uuid
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

from models import db, User, Song, Album, Rating, Genre
from app import app
from routes import auth_required, save_img, current_track


@app.route("/creator")
@auth_required
def creator():
    user = user = User.query.get(session["user_id"])
    genres = Genre.query.all()
    return render_template(
        "creator.html", user=user, current_track=current_track, genres=genres
    )


@app.route("/creator", methods=["POST"])
@auth_required
def creator_post():
    user = User.query.get(session["user_id"])

    if "song" in request.form:
        song_name = request.form.get("songname")
        lyrics = request.form.get("lyrics")
        songfile = request.files["songfile"]
        genre_id = request.form.get("genre")

        if not song_name:
            flash("Song name cannot be empty.", "danger")
            return redirect(url_for("creator"))

        if not songfile:
            flash("Song file cannot be empty.", "danger")
            return redirect(url_for("creator"))

        song_url = os.path.join(
            "tracks",
            str(uuid.uuid4().hex) + "_track.mp3",
        )

        songfile.save(os.path.join("static", song_url))

        song = Song(
            song_name=song_name,
            song_url=song_url,
            creator_id=user.id,
            lyrics=lyrics,
            genre_id=genre_id,
        )

        db.session.add(song)
        db.session.commit()
        flash("Track added successfully", "success")

    elif "album" in request.form:
        album_name = request.form.get("album_name")
        cover_file = request.files["cover"]

        if cover_file:
            album_cover_url = os.path.join(
                "albums",
                str(uuid.uuid4().hex) + "_album.jpg",
            )
            save_img(cover_file, os.path.join("static", album_cover_url))
            album = Album(
                album_name=album_name,
                creator_id=user.id,
                album_cover_url=album_cover_url,
            )
        else:
            album = Album(album_name=album_name, creator_id=user.id)

        db.session.add(album)

        for item in request.form:
            if item.split("-")[0] == "song":
                song_id = int(item.split("-")[1])
                song = Song.query.get(song_id)
                song.album_id = album.id

        db.session.commit()
        flash("Album created sucessfully", "success")

    elif "edit-song" in request.form:
        song_id = request.form.get("song-id")
        song_name = request.form.get("songname")
        lyrics = request.form.get("lyrics")
        genre_id = request.form.get("genre")
        song = Song.query.get(song_id)
        song.song_name = song_name
        song.lyrics = lyrics
        song.genre_id = genre_id
        db.session.commit()
        flash("Song updated successfully", "success")

    elif "edit-album" in request.form:
        album_id = request.form.get("album-id")
        album_name = request.form.get("album_name")
        cover_file = request.files["cover"]

        album = Album.query.get(album_id)
        album.album_name = album_name

        if cover_file:
            album_cover_url = os.path.join(
                "albums",
                str(uuid.uuid4().hex) + "_album.jpg",
            )
            save_img(cover_file, os.path.join("static", album_cover_url))
            album.album_cover_url = album_cover_url

        # for song in album.songs:
        #     db.session.delete(song)

        # for item in request.form:
        #     if item.split("-")[0] == "song":
        #         song_id = int(item.split("-")[1])
        #         song = Song.query.get(song_id)
        #         song.album_id = album.id

        db.session.commit()
        flash("Album updated successfully", "success")

    return redirect(url_for("creator"))


@app.route("/delete_album/<int:album_id>", methods=["GET"])
def delete_album(album_id):
    album = Album.query.get(album_id)

    for song in album.songs:
        song.album_id = None

    db.session.delete(album)
    db.session.commit()

    flash("Album deleted successfully", "success")
    return redirect(request.referrer)


@app.route("/delete_song/<int:song_id>", methods=["GET"])
def delete_song(song_id):
    song = Song.query.get(song_id)
    album = song.album

    ratings = Rating.query.filter_by(song_id=song_id).all()
    for rating in ratings:
        db.session.delete(rating)

    if album:
        album.songs.remove(song)
        db.session.commit()

        if not album.songs:
            db.session.delete(album)
            db.session.commit()

    db.session.delete(song)
    db.session.commit()

    flash("Song deleted successfully", "success")
    return redirect(request.referrer)
