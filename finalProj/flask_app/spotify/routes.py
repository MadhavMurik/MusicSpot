import base64,io
from io import BytesIO
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import spotify_client
from ..forms import SearchForm
from ..models import User


spotify = Blueprint("spotify", __name__)


def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image



@spotify.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = spotify_client.search(query)
    except ValueError as e:
        return render_template("query.html", error_msg=str(e))

    return render_template("query.html", results=results)

@spotify.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    if user:
        img = get_b64_img(user.username)
        
        top_artists = spotify_client.get_user_top_artists(limit=5)
        top_tracks = spotify_client.get_user_top_tracks(limit=5)
        top_genres = spotify_client.get_user_top_genres(limit=5)

        return render_template('user_profile.html', image=img, top_artists=top_artists, top_tracks=top_tracks, top_genres=top_genres)
    else:
        return render_template('user_profile.html', error='User not found!')
