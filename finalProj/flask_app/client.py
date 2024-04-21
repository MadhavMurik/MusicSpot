import requests
from collections import Counter
from .config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET


class Track(object):
    def __init__(self, spotify_json, detailed=False):
        if detailed:
            self.artists = [artist["name"]
                            for artist in spotify_json["artists"]]
            self.album = spotify_json["album"]["name"]
            self.release_date = spotify_json["album"]["release_date"]
            self.preview_url = spotify_json["preview_url"]

        self.name = spotify_json["name"]
        self.popularity = spotify_json["popularity"]
        self.id = spotify_json["id"]
        self.type = "Track"
        self.image_url = spotify_json["album"]["images"][0]["url"]

    def __repr__(self):
        return self.name


class SpotifyClient(object):
    def __init__(self, client_id, client_secret):
        self.sess = requests.Session()
        self.base_url = "https://api.spotify.com/v1/"
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        auth_url = "https://accounts.spotify.com/api/token"
        auth_resp = requests.post(
            auth_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        if auth_resp.status_code != 200:
            raise ValueError("Failed to authenticate with Spotify API")

        return auth_resp.json()["access_token"]

    def search(self, search_string):
        """
        Searches the Spotify API for the supplied search_string, and returns
        a list of dictionaries containing track name, Spotify track URL, and track image URL.
        """
        search_string = "%20".join(search_string.split())
        search_url = f"search?q={search_string}&type=track"

        resp = self.sess.get(
            self.base_url + search_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        if resp.status_code != 200:
            raise ValueError(
                "Search request failed; make sure your client ID and secret are correct"
            )

        data = resp.json()

        if "error" in data:
            raise ValueError(f'[ERROR]: Error retrieving results: \'{data["error"]["message"]}\' ')


        search_results_json = data["tracks"]["items"]

        result = []
        for track in search_results_json:
            track_name = track["name"]
            track_url = track["external_urls"]["spotify"]
            track_image_url = track["album"]["images"][0]["url"] if track["album"]["images"] else None
            result.append({"name": track_name, "url": track_url,
                          "image_url": track_image_url})

        return result

    def get_user_top_artists(self, sp, limit=6):
        """
        :return: A list of dictionaries containing top artist information including cover image, artist profile, and Spotify link.
        """
        top_artists = sp.current_user_top_artists(limit=limit)
        artists_info = []
        for item in top_artists['items']:
            artist_info = {
                'name': item['name'],
                # Get the first image if available
                'image': item['images'][0]['url'] if item['images'] else None,
                # Spotify artist profile link
                'profile': item['external_urls']['spotify'],
            }
            artists_info.append(artist_info)
        return artists_info


    def get_user_top_tracks(self, sp, limit=5):
        """
        :return: A list of dictionaries containing top track information including cover image and Spotify link.
        """
        top_tracks = sp.current_user_top_tracks(limit=limit)
        tracks_info = []
        for item in top_tracks['items']:
            track_info = {
                'name': item['name'],
                # Assuming only one artist per track
                'artist': item['artists'][0]['name'],
                # Get the first image if available
                'image': item['album']['images'][0]['url'] if item['album']['images'] else None,
                # Spotify track link
                'spotify_link': item['external_urls']['spotify'],
            }
            tracks_info.append(track_info)
        return tracks_info
    
    
    def get_user_top_genres(self, sp, limit=5):
        """
        :return: A list of Track objects containing top genres information.
        """
        top_artists = sp.current_user_top_artists(limit=limit)
        # Extracting genres from top artists
        genres = [genre for artist in top_artists['items']
                for genre in artist['genres']]
        # Capitalizing first letter of each word in genres
        capitalized_genres = [genre.capitalize() for genre in genres]
        # Counting occurrences of each genre
        genre_counts = Counter(capitalized_genres)
        # Sorting genres by count
        top_genres = genre_counts.most_common(limit)
        return [genre[0] for genre in top_genres]



## -- Example usage -- ###
if __name__ == "__main__":
    import os

    client_id = SPOTIFY_CLIENT_ID
    client_secret = SPOTIFY_CLIENT_SECRET

    if client_id is None or client_secret is None:
        raise ValueError(
            "SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET environment variables are not set")

    client = SpotifyClient(client_id, client_secret)

    tracks = client.search("lil")

    for track in tracks:
        print(track)

    print(len(tracks))
