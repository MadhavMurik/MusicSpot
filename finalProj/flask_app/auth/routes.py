from flask import Blueprint, redirect, request, session, render_template, url_for
from ..config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import urlencode
from flask_login import current_user, login_required, login_user, logout_user
from ..models import User
from .. import spotify_client


auth = Blueprint('auth', __name__)

# Spotify API credentials
SPOTIFY_CLIENT_ID = SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = SPOTIFY_CLIENT_SECRET
SPOTIFY_REDIRECT_URI = 'https://music-spot-two.vercel.app/callback'
SCOPE = 'user-top-read'

# Spotipy OAuth object
sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                        client_secret=SPOTIFY_CLIENT_SECRET,
                        redirect_uri=SPOTIFY_REDIRECT_URI,
                        scope=SCOPE)


@auth.route('/connect')
def connect():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@auth.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('.top_tracks'))

@auth.route('/top_tracks')
def top_tracks():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('.connect'))

    sp = spotipy.Spotify(auth=token_info['access_token'])

    top_tracks = spotify_client.get_user_top_tracks(sp)
    top_genres = spotify_client.get_user_top_genres(sp)
    top_artists = spotify_client.get_user_top_artists(sp)

    return render_template('user_profile.html', top_tracks=top_tracks, top_genres=top_genres, top_artists=top_artists)
