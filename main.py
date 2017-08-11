from datetime import datetime, timedelta

from spotipy import Spotify
import spotipy.util

import settings


class Song(object):

    def __init__(self, track_id, played_at, artist_id, artist_name, track_name):
        self.id = track_id
        self.played_at = played_at
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.track_name = track_name

    @property
    def csv_string(self):
        fields = [self.id, self.played_at, self.artist_id, self.artist_name, self.track_name]
        escaped_fields = [str(field).replace(',', '') for field in fields]
        return ",".join(escaped_fields)


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
            song = Song(track_id= item['track']['id'],
                        played_at=convert_played_at_to_datetime(item['played_at']),
                        artist_id=item['track']['artists'][0]['id'],
                        artist_name=item['track']['artists'][0]['name'],
                        track_name=item['track']['name'])
            songs.append(song)
        return songs

    def get_recently_played_songs(self, limit=50):
        songs = []
        response = self.client._get('me/player/recently-played', after=1502311849, limit=limit)
        songs.extend(self._get_songs_from_response(response))
        if 'next' in response:
            response = self.client.next(response)
            songs.extend(self._get_songs_from_response(response))
        print("Loaded last {} played songs.".format(len(songs)))
        return songs


def pad_number(number):
    return "0{}".format(number)[-2:]


def get_run_name():
    now = datetime.now()
    return "run_{}-{}-{}_{}-{}-{}".format(pad_number(now.year),
                                          pad_number(now.month),
                                          pad_number(now.day),
                                          pad_number(now.hour),
                                          pad_number(now.minute),
                                          pad_number(now.second))


def write_songs_to_csv(songs, run_name):
    file_path = '{}/{}.csv'.format(settings.PATH_TO_DATA_REPO, run_name)
    print("Writing file {}.".format(file_path))
    with open(file_path, 'w') as f:
        f.write("Track_ID,Played_At,Artist_ID,Artist_Name,Track_Name\n")
        for song in songs:
            f.write("{}\n".format(song.csv_string))


def main():
    run_name = get_run_name()
    print("Starting run {}".format(run_name))
    s = SpotifyConnection(scope='user-read-recently-played')
    songs = s.get_recently_played_songs()
    write_songs_to_csv(songs, run_name)
    print("Bye.")


if __name__ == '__main__':
    main()
