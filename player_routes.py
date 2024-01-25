from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
import os
from models import db, User, Song, Album, Rating
from app import app
from sqlalchemy.orm import make_transient
from threading import Thread
import pygame

pygame.mixer.init()
current_track = {"song": None, "artist": None, "album": None, "length": None}


def play_music(song_id, length):
    with app.app_context():
        song = Song.query.get(song_id)
        song_url = os.path.join("static", song.song_url)
        make_transient(song)
        current_track["song"] = song

        artist = User.query.get(song.creator_id)
        make_transient(artist)
        current_track["artist"] = artist

        if song.album:
            album = Album.query.get(song.album.id)
            make_transient(album)
            current_track["album"] = album

        Song.query.get(song_id).plays += 1
        db.session.commit()

        pygame.mixer.music.load(song_url)
        pygame.mixer.music.play()

    current_track["length"] = length


def pause_music():
    pygame.mixer.music.pause()


def stop_music():
    print("stoooooooop")
    pygame.mixer.music.stop()
    current_track["song"] = None
    current_track["artist"] = None
    current_track["album"] = None
    current_track["length"] = None


@app.route("/get_seconds_played")
def get_seconds_played_route():
    sec = pygame.mixer.music.get_pos() / 1000
    formatted_pos = "{:02}:{:02}".format(*divmod(int(sec), 60))
    return jsonify({"current_seconds_played": formatted_pos})


@app.route("/play", methods=["GET", "POST"])
def play():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "play":
            pygame.mixer.music.unpause()
        else:
            pause_music()
    else:
        action = request.args.get("action")

        if action == "play":
            song_id = request.args.get("song_id")
            song = Song.query.get(song_id)

            if current_track["song"] and current_track["song"].id == song_id:
                pygame.mixer.music.unpause()
            else:
                stop_music()
                song_url = os.path.join("static", song.song_url)
                length = pygame.mixer.Sound(song_url).get_length()
                formatted_len = "{:02}:{:02}".format(*divmod(int(length), 60))
                Thread(target=play_music, args=(song_id, formatted_len)).start()
        elif action == "pause":
            pause_music()

    return redirect(request.referrer)


from models import Genre
from routes import auth_required, current_track


# Route to handle the search
@app.route("/search", methods=["GET", "POST"])
@auth_required
def search_songs():
    results = Song.query.all()
    # print('genre' in request.args.keys())
    if "search" in request.args.keys():
        search_query = request.args.get("search", "")
        results = Song.query.filter(Song.song_name.ilike(f"%{search_query}%")).all()

    elif "genre" in request.args.keys():
        genre_id = request.args.get("genre", "")
        results = Song.query.filter_by(genre_id=genre_id).all()

    user = User.query.get(session["user_id"])
    genres = Genre.query.all()

    return render_template(
        "search.html",
        results=results,
        user=user,
        current_track=current_track,
        genres=genres,
    )


@app.route("/search", methods=["POST"])
@auth_required
def search_genre():
    print("hoooooooooo")
    return redirect(url_for("search"))
