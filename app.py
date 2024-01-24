from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

import config
import models

import player_routes
import routes
import playlist_routes
import creator_routes