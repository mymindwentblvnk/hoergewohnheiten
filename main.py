from datetime import datetime, timedelta
import os
import glob

from spotipy import Spotify
import spotipy.util

import pyowm

from git import Repo

import settings


YEAR = datetime.now().year
MONTH = datetime.now().month

CSV_HEADER = "played_at_as_utc,track_id,track_name,track_bpm,track_energy,track_valence,artist_id,artist_name,artist_genres,album_id,album_name,album_label,album_genres,weather_temperature,weather_status"


def convert_datetime_to_utc_in_ms(dt):
    neunzehnhundertsiebzig = datetime.utcfromtimestamp(0)
    return int((dt - neunzehnhundertsiebzig).total_seconds() * 1000)


def convert_played_at_to_datetime(played_at, date_format):
    return datetime.strptime(played_at, date_format)


def convert_played_at_from_csv_to_datetime(played_at):
    try:
        return convert_played_at_to_datetime(played_at, date_format='%Y-%m-%d %H:%M:%S.%f')
    except:
        # For the single moment where the played at time hits a full second
        return convert_played_at_to_datetime(played_at, date_format='%Y-%m-%d %H:%M:%S')


def convert_played_at_from_response_to_datetime(played_at):
    try:
        return convert_played_at_to_datetime(played_at, date_format='%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        # For the single moment where the played at time hits a full second
        return datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%SZ')


def get_last_imported_datetime_as_utc():
    csv_file_pattern = '{}/[0-9][0-9][0-9][0-9]-[0-9][0-9].csv'.format(settings.PATH_TO_DATA_REPO)
    for csv_file in sorted(glob.glob(csv_file_pattern), reverse=True):
        try:
            print(csv_file)
            with open(csv_file, 'r') as f:
                lines = f.readlines()
                last_line = lines[-1]
                played_at = last_line.split(',')[0]
                dt = convert_played_at_from_csv_to_datetime(played_at)
                return convert_datetime_to_utc_in_ms(dt)
        except (FileNotFoundError, IndexError):
            pass


def pad_number(number):
    return "0{}".format(number)[-2:]


def write_tracks_to_csv(tracks, csv_file_path):
    print("Writing file {}.".format(csv_file_path))

    initial_write = False if os.path.exists(csv_file_path) else True

    with open(csv_file_path, 'a') as f:
        if initial_write:
            f.write("{}\n".format(CSV_HEADER))
        for track in reversed(tracks):  # Reverse tracks so latest play is at the bottom
            f.write("{}\n".format(track.csv_string))


def git_push_csv(csv_file_path):
    print("Pushing file to GitHub.")
    repo = Repo(settings.PATH_TO_DATA_REPO)
    repo.index.add([csv_file_path])
    repo.index.commit("Updating {}".format(csv_file_path.split('/')[-1]))
    repo.remote('origin').push()


class Track(object):

    def __init__(self,
                 played_at,
                 track_id,
                 track_name,
                 track_bpm,
                 track_energy,
                 track_valence,
                 artist_id,
                 artist_name,
                 artist_genres,
                 album_id,
                 album_name,
                 album_label,
                 album_genres,
                 weather_temperature,
                 weather_status):
        self.played_at = played_at
        self.track_id = track_id
        self.track_name = track_name
        self.track_bpm = track_bpm
        self.track_energy = track_energy
        self.track_valence = track_valence
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.artist_genres = artist_genres
        self.album_id = album_id
        self.album_name = album_name
        self.album_label = album_label
        self.album_genres = album_genres
        self.weather_temperature=weather_temperature
        self.weather_status=weather_status

    @property
    def csv_string(self):
        fields = [self.played_at,
                  self.track_id,
                  self.track_name,
                  self.track_bpm,
                  self.track_energy,
                  self.track_valence,
                  self.artist_id,
                  self.artist_name,
                  self.artist_genres,
                  self.album_id,
                  self.album_name,
                  self.album_label,
                  self.album_genres,
                  self.weather_temperature,
                  self.weather_status]
        escaped_fields = [str(field).replace(',', '').replace('\'', '').replace('\"', '') for field in fields]
        return ",".join(escaped_fields)


class HoergewohnheitenManager(object):

    def __init__(self):
        token = spotipy.util.prompt_for_user_token(settings.SPOTIFY_USER_NAME,
                                                   scope='user-read-recently-played',
                                                   client_id=settings.SPOTIFY_CLIENT_ID,
                                                   client_secret=settings.SPOTIFY_CLIENT_SECRET,
                                                   redirect_uri=settings.SPOTIFY_REDIRECT_URI)
        self.client = Spotify(auth=token)
        self.owm = pyowm.OWM(settings.OPEN_WEATHER_MAP_API_KEY)
        self.audio_feature_cache = {}
        self.album_cache = {}
        self.artist_cache = {}

    def get_temperature_and_weather_status(self):
        try:
            observation = self.owm.weather_at_id(settings.OPEN_WATHER_MAP_NUREMBERG_ID)
            weather = observation.get_weather()
            temperature = weather.get_temperature(unit='celsius')['temp']
            weather_status = weather.get_detailed_status()
            return temperature, weather_status
        except:
            print("Weather could not be loaded.")
            return '',''

    def get_audio_feature(self, track_id):
        if track_id not in self.audio_feature_cache:
            audio_feature = self.client.audio_features(track_id)
            self.audio_feature_cache[track_id] = audio_feature[0]
        return self.audio_feature_cache[track_id]

    def get_album(self, album_id):
        if album_id not in self.album_cache:
            response = self.client.album(album_id)
            self.album_cache[album_id] = response
        return self.album_cache[album_id]

    def get_artist(self, artist_id):
        if artist_id not in self.artist_cache:
            response = self.client.artist(artist_id)
            self.artist_cache[artist_id] = response
        return self.artist_cache[artist_id]

    def _stringify_lists(self, list_items):
        return "|".join(list_items) if list_items else ''

    def create_tracks_from_response(self, response):
        tracks = []

        # Get weather for this run
        temperature, weather_status = self.get_temperature_and_weather_status()

        for item in response['items']:
            # Get audio features
            audio_feature = self.get_audio_feature(item['track']['id'])
            bpm = audio_feature['tempo']
            energy = audio_feature['energy']
            valence = audio_feature['valence']

            # Get artist information
            artist = self.get_artist(item['track']['artists'][0]['id'])
            artist_genres = self._stringify_lists(artist['genres'])

            # Get album information
            album = self.get_album(item['track']['album']['id'])
            label = album['label']
            album_genres = self._stringify_lists(album['genres'])

            track = Track(played_at=convert_played_at_from_response_to_datetime(item['played_at']),
                          track_id= item['track']['id'],
                          track_name=item['track']['name'],
                          track_bpm=bpm,
                          track_energy=energy,
                          track_valence=valence,
                          artist_id=item['track']['artists'][0]['id'],
                          artist_name=item['track']['artists'][0]['name'],
                          artist_genres=artist_genres,
                          album_id=item['track']['album']['id'],
                          album_name=item['track']['album']['name'],
                          album_label=label,
                          album_genres=album_genres,
                          weather_temperature=temperature,
                          weather_status=weather_status)
            tracks.append(track)
        return tracks

    def get_recently_played_tracks(self, limit=50, after=None):
        tracks = []
        response = self.client._get('me/player/recently-played', after=after, limit=limit)
        tracks.extend(self.create_tracks_from_response(response))
        if 'next' in response:
            response = self.client.next(response)
            tracks.extend(self.create_tracks_from_response(response))
        return tracks


def main():
    print("Starting run at {}".format(datetime.now()))
    print(50 * "-")

    # Get last imported datetime
    last_imported_datetime_as_utc = get_last_imported_datetime_as_utc()

    # Load tracks
    mgr = HoergewohnheitenManager()
    tracks = mgr.get_recently_played_tracks(after=last_imported_datetime_as_utc)
    print("Loaded last {} played tracks.".format(len(tracks)))

    if tracks:
        file_path = '{}/{}-{}.csv'.format(settings.PATH_TO_DATA_REPO,
                                          YEAR,
                                          pad_number(MONTH))
        write_tracks_to_csv(tracks, file_path)
        git_push_csv(file_path)

    print(50 * "-")
    print("Bye.")


if __name__ == '__main__':
    main()
