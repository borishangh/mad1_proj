from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import app

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pfp_url = db.Column(db.String(255), default="default_pfp.jpg")

    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    passhash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.String(10), default=datetime.now().strftime("%B %Y"))

    songs = db.relationship("Song", backref="user", lazy=True)
    albums = db.relationship("Album", backref="user", lazy=True)
    playlists = db.relationship("Playlist", backref="user", lazy=True)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)


class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Album(db.Model):
    __tablename__ = "albums"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    album_name = db.Column(db.String(255), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    album_cover_url = db.Column(db.String(255), default="default_album.jpg")
    created = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with songs
    songs = db.relationship("Song", backref="album", lazy=True)


class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    song_name = db.Column(db.String(255), nullable=False)
    song_url = db.Column(db.String(255), nullable=False)

    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey("albums.id"))
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"))

    created_at = db.Column(db.String(10), default=datetime.now().strftime("%B %Y"))

    lyrics = db.Column(db.Text)
    plays = db.Column(db.Integer, default=0)

    ratings = db.relationship("Rating", backref="song", lazy=True)


class Rating(db.Model):
    __tablename__ = "ratings"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    song_id = db.Column(db.Integer, db.ForeignKey("songs.id"), nullable=False)

    five_star = db.Column(db.Integer, default=0)
    four_star = db.Column(db.Integer, default=0)
    three_star = db.Column(db.Integer, default=0)
    two_star = db.Column(db.Integer, default=0)
    one_star = db.Column(db.Integer, default=0)


playlist_songs = db.Table(
    "playlist_songs",
    db.Column(
        "playlist_id", db.Integer, db.ForeignKey("playlists.id"), primary_key=True
    ),
    db.Column("song_id", db.Integer, db.ForeignKey("songs.id"), primary_key=True),
)


class Playlist(db.Model):
    __tablename__ = "playlists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    cover_url = db.Column(db.String(255), default="default_playlist.jpg")
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    songs = db.relationship(
        "Song", secondary=playlist_songs, backref="playlists", lazy="dynamic"
    )


with app.app_context():
    db.create_all()

    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            username="admin", password="admin", email="admin@admin", is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

    genres = ["Rock", "Pop", "Hip Hop", "Electronic", "Jazz", "Country", "Classical"]
    for genre_name in genres:
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)
            db.session.commit()
