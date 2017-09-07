from datetime import datetime, timedelta
import os
import glob

from git import Repo

import pandas

import settings

from connections import OWMConnection, SpotifyConnection


CSV_HEADER = "played_at_as_utc,track_id,track_name,track_bpm,track_energy,track_valence,artist_id,artist_name,artist_genres,album_id,album_name,album_label,album_genres,weather_temperature,weather_status"


class PlayedTrack(object):

    def __init__(self,
                 played_at,
                 track_id,
                 track_name,
                 track_tempo,
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
        self.track_tempo = track_tempo
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
                  self.track_tempo,
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


def convert_datetime_to_utc_in_ms(dt):
    neunzehnhundertsiebzig = datetime.utcfromtimestamp(0)
    return int((dt - neunzehnhundertsiebzig).total_seconds() * 1000)


def convert_played_at_from_csv_to_datetime(played_at):
    try:
        return datetime.strptime(played_at, '%Y-%m-%d %H:%M:%S.%f')
    except:
        # For the single moment where the played at time hits a full second
        return datetime.strptime(played_at, '%Y-%m-%d %H:%M:%S')


def get_last_imported_datetime_as_utc():
    csv_file_pattern = '{}/[0-9][0-9][0-9][0-9]-[0-9][0-9].csv'.format(settings.PATH_TO_DATA_REPO)
    for csv_file in sorted(glob.glob(csv_file_pattern), reverse=True):
        try:
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


class HoergewohnheitenStats(object):

    def __init__(self, csv_file_path):
        self.spotify = SpotifyConnection()
        self.data_frame = pandas.read_csv(csv_file_path)

    @property
    def top_tracks(self):
        top_tracks = data_frame.groupby('track_id').size().sort_values(ascending=False)[:TOP_N]
        for track_id in top_tracks.keys():
            pass

    @property
    def top_artists(self):
        top_artists = data_frame.groupby('artist_id').size().sort_values(ascending=False)[:TOP_N]

    @property
    def top_albums(self):
        top_albums = data_frame.groupby('album_id').size().sort_values(ascending=False)[:TOP_N]

    def write_markdown(self):
        pass


class HoergewohnheitenManager(object):

    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.spotify = SpotifyConnection()
        self.weather = OWMConnection().get_weather()
        self.csv_file_path = '{}/{}-{}.csv'.format(settings.PATH_TO_DATA_REPO,
                                                   self.year,
                                                   pad_number(self.month))

    def _stringify_lists(self, list_items):
        return "|".join(list_items) if list_items else ""

    def track_to_played_track(self, track):
        played_track = PlayedTrack(played_at=track.played_at,
                                   track_id=track.track_id,
                                   track_name=track.track_name,
                                   track_tempo=track.audio_feature.tempo,
                                   track_energy=track.audio_feature.energy,
                                   track_valence=track.audio_feature.valence,
                                   artist_id=track.artist.artist_id,
                                   artist_name=track.artist.artist_name,
                                   artist_genres=self._stringify_lists(track.artist.artist_genres),
                                   album_id=track.album.album_id,
                                   album_name=track.album.album_name,
                                   album_label=track.album.label,
                                   album_genres=self._stringify_lists(track.album.album_genres),
                                   weather_temperature=self.weather.temperature,
                                   weather_status=self.weather.status)
        return played_track

    def process_tracks(self, last_imported_datetime):
        tracks = self.spotify.get_recently_played_tracks(after=last_imported_datetime)
        played_tracks = [self.track_to_played_track(track) for track in tracks]

        print("Loaded last {} played tracks.".format(len(played_tracks)))

        if played_tracks:
            write_tracks_to_csv(played_tracks, self.csv_file_path)
            git_push_csv(self.csv_file_path)

    def process_stats(self):
        stats = HoergewohnheitenStats(self.csv_file_path)
        pass


if __name__ == '__main__':
    now = datetime.now()
    print("Starting run at {}".format(now))

    # Get last imported datetime
    last_imported_datetime_as_utc = get_last_imported_datetime_as_utc()

    mgr = HoergewohnheitenManager(year=now.year, month=now.month)
    # Process tracks
    mgr.process_tracks(last_imported_datetime=last_imported_datetime_as_utc)
    # Process stats
    mgr.process_stats()

    print("Bye.")
