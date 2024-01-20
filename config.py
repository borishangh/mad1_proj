import os
from dotenv import load_dotenv
from app import app

load_dotenv()


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = os.getenv(
    "SQLALCHEMY_TRACK_NOTIFICATIONS"
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")
