import settings

from spotipy import Spotify
import spotipy.util

from datetime import datetime, timedelta


class Song(object):

    def __init__(self, id, played_at, artist_name, track_name):
        self.id = id
        self.played_at = played_at
        self.artist_name = artist_name
        self.track_name = track_name

    @property
    def csv_string(self):
        fields = [self.id, self.played_at, self.artist_name, self.track_name]
        escaped_fields = [str(field).replace('"', '\\"') for field in fields]
        return ",".join(['"{}"'.format(field) for field in escaped_fields])


def convert_played_at_to_datetime(played_at):
    played_at_without_timezone = datetime.strptime(played_at, "%Y-%m-%dT%H:%M:%S.%fZ") 
    played_at_with_timezone = played_at_without_timezone + timedelta(hours=2)
    return played_at_with_timezone


class SpotifyConnection(object):

    def __init__(self, scope):
        token = spotipy.util.prompt_for_user_token(settings.SPOTIFY_USER_NAME,
                                                   scope=scope,
                                                   client_id=settings.SPOTIFY_CLIENT_ID,
                                                   client_secret=settings.SPOTIFY_CLIENT_SECRET,
                                                   redirect_uri=settings.SPOTIFY_REDIRECT_URI)
        self.client = Spotify(auth=token)

    def _get_songs_from_response(self, response):
        songs = []
        for item in response['items']:
            song = Song(id= item['track']['id'],
                        played_at=convert_played_at_to_datetime(item['played_at']),
                        artist_name=item['track']['artists'][0]['name'],
                        track_name=item['track']['name'])
            songs.append(song)
        return songs

    def get_recently_played_songs(self, limit=50):
        recently_played = []
        response = self.client._get('me/player/recently-played', limit=limit)
        recently_played.extend(self._get_songs_from_response(response))
        if 'next' in response:
            response = self.client.next(response)
            recently_played.extend(self._get_songs_from_response(response))
        return recently_played


def main():
    s = SpotifyConnection(scope='user-read-recently-played')
    songs = s.get_recently_played_songs()

    # Create CSV
    for song in songs:
        print(song.csv_string)


if __name__ == '__main__':
    main()
