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
from models import db, User, Song, Album, Rating
from app import app

from threading import Thread
import pygame

pygame.mixer.init()
current_track = {"file": None, "title": None, "length": None}


def play_music(file, title, length):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    current_track["file"] = file
    current_track["title"] = title
    current_track["length"] = length


def pause_music():
    pygame.mixer.music.pause()


def stop_music():
    pygame.mixer.music.stop()
    current_track["file"] = None
    current_track["title"] = None
    current_track["length"] = None


@app.route("/get_seconds_played")
def get_seconds_played_route():
    ms = pygame.mixer.music.get_pos() / 1000
    formatted_pos = "{:02}:{:02}".format(*divmod(int(ms), 60))
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
        song_id = request.args.get("song_id")

        if action == "pause":
            pause_music()
        elif action == "play":
            song = Song.query.get(song_id)
            title = song.song_name
            file_path = song.song_url

            if current_track["file"] == file_path:
                pygame.mixer.music.unpause()
            else:
                stop_music()
                length = pygame.mixer.Sound(file_path).get_length()
                formatted_len = "{:02}:{:02}".format(*divmod(int(length), 60))
                Thread(target=play_music, args=(file_path, title, formatted_len)).start()

    return redirect(request.referrer)


@app.route("/stop", methods=["POST"])
def stop():
    stop_music()
    return redirect(url_for("index"))
