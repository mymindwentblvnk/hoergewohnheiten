from datetime import datetime, timedelta
import os
import pickle

from spotipy import Spotify
import spotipy.util

from git import Repo

import settings


YEAR = datetime.now().year
MONTH = datetime.now().month


def convert_played_at_to_datetime(played_at, date_format='%Y-%m-%dT%H:%M:%S.%fZ'):
    try:
        return datetime.strptime(played_at, date_format)
    except:
        return datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%SZ')


def get_last_imported_datetime_from_songs(songs):
    if songs:
        return max([s.played_at for s in songs])


def convert_datetime_to_utc_in_ms(dt):
    neunzehnhundertsiebzig = datetime.utcfromtimestamp(0)
    return int((dt - neunzehnhundertsiebzig).total_seconds() * 1000)


def get_last_imported_datetime_as_utc():
    try:
        last_imported_datetime = pickle.load(open(settings.LAST_IMPORTED_DATETIME_FILE_PATH, 'rb'))
        return convert_datetime_to_utc_in_ms(last_imported_datetime)
    except FileNotFoundError:
        print("No last imported datetime found at {}.".format(settings.LAST_IMPORTED_DATETIME_FILE_PATH))


def save_last_imported_datetime(last_imported_datetime):
    pickle.dump(last_imported_datetime, open(settings.LAST_IMPORTED_DATETIME_FILE_PATH, 'wb'))


def pad_number(number):
    return "0{}".format(number)[-2:]


def write_songs_to_csv(songs, csv_file_path):
    print("Writing file {}.".format(csv_file_path))

    initial_write = False if os.path.exists(csv_file_path) else True

    with open(csv_file_path, 'a') as f:
        if initial_write:
            f.write("played_at,track_id,track_name,artist_id,artist_name,album_id,album_name\n")
        for song in reversed(songs):  # Reverse songs so latest play is at the bottom
            f.write("{}\n".format(song.csv_string))


def git_push_csv(csv_file_path):
    print("Pushing file to GitHub.")
    repo = Repo(settings.PATH_TO_DATA_REPO)
    repo.index.add([csv_file_path])
    repo.index.commit("Updating/uploading {}".format(csv_file_path))
    repo.remote('origin').push()


class Song(object):

    def __init__(self,
                 played_at,
                 track_id,
                 artist_id,
                 artist_name,
                 track_name,
                 album_id,
                 album_name):
        self.played_at = played_at
        self.track_id = track_id
        self.track_name = track_name
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.album_id = album_id
        self.album_name = album_name

    @property
    def csv_string(self):
        fields = [self.played_at,
                  self.track_id,
                  self.track_name,
                  self.artist_id,
                  self.artist_name,
                  self.album_id,
                  self.album_name]
        escaped_fields = [str(field).replace(',', '').replace('\'', '').replace('\"', '') for field in fields]
        return ",".join(escaped_fields)


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
            song = Song(played_at=convert_played_at_to_datetime(item['played_at']),
                        track_id= item['track']['id'],
                        track_name=item['track']['name'],
                        artist_id=item['track']['artists'][0]['id'],
                        artist_name=item['track']['artists'][0]['name'],
                        album_id=item['track']['album']['id'],
                        album_name=item['track']['album']['name'])
            songs.append(song)
        return songs

    def get_recently_played_songs(self, limit=50, after=None):
        songs = []
        response = self.client._get('me/player/recently-played', after=after, limit=limit)
        songs.extend(self._get_songs_from_response(response))
        if 'next' in response:
            response = self.client.next(response)
            songs.extend(self._get_songs_from_response(response))
        return songs


def main():
    print("Starting run at {}".format(datetime.now()))
    print(50 * "-")

    # Get last imported datetime
    last_imported_datetime_as_utc = get_last_imported_datetime_as_utc()

    # Load songs
    s = SpotifyConnection(scope='user-read-recently-played')
    songs = s.get_recently_played_songs(after=last_imported_datetime_as_utc)
    print("Loaded last {} played songs.".format(len(songs)))

    if songs:
        file_path = '{}/{}-{}.csv'.format(settings.PATH_TO_DATA_REPO,
                                          YEAR,
                                          pad_number(MONTH))
        write_songs_to_csv(songs, file_path)
        git_push_csv(file_path)

        # Save last imported datetime
        last_imported_datetime = get_last_imported_datetime_from_songs(songs)
        save_last_imported_datetime(last_imported_datetime)
    print("Bye.")


if __name__ == '__main__':
    main()
