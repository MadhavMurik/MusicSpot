# 3rd-party packages
from flask import Flask, render_template
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
from .config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# local
from .client import SpotifyClient

# Update with your Client ID and Client Secret
SPOTIFY_CLIENT_ID = SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = SPOTIFY_CLIENT_SECRET

os.environ['SPOTIFY_CLIENT_ID'] = SPOTIFY_CLIENT_ID
os.environ['SPOTIFY_CLIENT_SECRET'] = SPOTIFY_CLIENT_SECRET

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
spotify_client = SpotifyClient(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

from .users.routes import users
from .spotify.routes import spotify
from .auth.routes import auth

def custom_404(e):
    return render_template("404.html"), 404

def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(spotify)
    app.register_blueprint(auth)
    app.register_error_handler(404, custom_404)

    login_manager.login_view = "users.login"


    return app
