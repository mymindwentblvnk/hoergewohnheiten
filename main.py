from datetime import datetime, timedelta
import os
import glob
import json

from git import Repo
import pandas as pd

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


class HoergewohnheitenStats(object):

    def __init__(self, csv_file_path):
        self.spotify = SpotifyConnection()
        self.data_frame = pd.read_csv(csv_file_path)
        self.times = self._get_times()
        self.top_n = 15

    def _get_times(self):
        times = pd.to_datetime(self.data_frame.played_at_as_utc)
        return times + pd.Timedelta('{}:00:00'.format(pad_number(settings.HOURS_FROM_UTC)))

    def top_tracks(self):
        result = {}
        top_tracks = self.data_frame.groupby('track_id').size().sort_values(ascending=False)[:self.top_n]
        for index, track_id in enumerate(top_tracks.keys(), 1):
            track = self.spotify.get_track(track_id)
            result[index] = {}
            result[index]['plays'] = int(top_tracks[track_id])
            result[index]['track'] = {}
            result[index]['track']['id'] = track.track_id
            result[index]['track']['name'] = track.track_name
            result[index]['artist'] = {}
            result[index]['artist']['id'] = track.artist.artist_id
            result[index]['artist']['name'] = track.artist.artist_name
            result[index]['album'] = {}
            result[index]['album']['id'] = track.album.album_id
            result[index]['album']['name'] = track.album.album_name
        return result

    def top_artists(self):
        result = {}
        top_artists = self.data_frame.groupby('artist_id').size().sort_values(ascending=False)[:self.top_n]
        for index, artist_id in enumerate(top_artists.keys(), 1):
            artist = self.spotify.get_artist(artist_id)
            result[index] = {}
            result[index]['plays'] = int(top_artists[artist_id])
            result[index]['artist'] = {}
            result[index]['artist']['id'] = artist.artist_id
            result[index]['artist']['name'] = artist.artist_name
        return result

    def top_albums(self):
        result = {}
        top_albums = self.data_frame.groupby('album_id').size().sort_values(ascending=False)[:self.top_n]
        for index, album_id in enumerate(top_albums.keys(), 1):
            album = self.spotify.get_album(album_id)
            result[index] = {}
            result[index]['plays'] = int(top_albums[album_id])
            result[index]['album'] = {}
            result[index]['album']['id'] = album.album_id
            result[index]['album']['name'] = album.album_name
            result[index]['album']['artist'] = {}
            result[index]['album']['artist']['id'] = album.artist.artist_id
            result[index]['album']['artist']['name'] = album.artist.artist_name
        return result

    def plays(self):
        return len(self.data_frame)

    def bpm_mean(self):
        return round(self.data_frame['track_bpm'].mean(), 2)

    def energy_mean(self):
        return round(self.data_frame['track_energy'].mean(), 2)

    def valence_mean(self):
        return round(self.data_frame['track_valence'].mean(), 2)

    def bpm_by_hour_of_day(self):
        result = {}
        mean_by_hour_of_day = self.data_frame.groupby([self.times.dt.hour])['track_bpm'].mean()
        for hour in mean_by_hour_of_day.keys():
            result[int(hour)] = round(mean_by_hour_of_day[hour], 2)
        return result

    def energy_by_hour_of_day(self):
        result = {}
        mean_by_hour_of_day = self.data_frame.groupby([self.times.dt.hour])['track_energy'].mean()
        for hour in mean_by_hour_of_day.keys():
            result[int(hour)] = round(mean_by_hour_of_day[hour], 2)
        return result

    def valence_by_hour_of_day(self):
        result = {}
        mean_by_hour_of_day = self.data_frame.groupby([self.times.dt.hour])['track_valence'].mean()
        for hour in mean_by_hour_of_day.keys():
            result[int(hour)] = round(mean_by_hour_of_day[hour], 2)
        return result

    @property
    def as_dict(self):
        return {
            'avg_bpm': self.bpm_mean(),
            'avg_energy': self.energy_mean(),
            'avg_valence': self.valence_mean(),
            'by_hour_bpm': self.bpm_by_hour_of_day(),
            'by_hour_energy': self.energy_by_hour_of_day(),
            'by_hour_valence': self.valence_by_hour_of_day(),
            'plays': self.plays(),
            'top_tracks': self.top_tracks(),
            'top_artists': self.top_artists(),
            'top_albums': self.top_albums(),
        }


class HoergewohnheitenManager(object):

    def __init__(self, year=None, month=None):
        self.year = year if year else datetime.now().year
        self.month = month if month else datetime.now().month
        self.spotify = SpotifyConnection()
        self.weather = OWMConnection().get_weather()
        self.csv_file_path = '{}/{}-{}.csv'.format(settings.PATH_TO_DATA_REPO,
                                                   self.year,
                                                   pad_number(self.month))
        self.json_file_path = '{}/{}-{}.json'.format(settings.PATH_TO_DATA_REPO,
                                                     self.year,
                                                     pad_number(self.month))

    def _stringify_lists(self, list_items):
        return "|".join(list_items) if list_items else ""

    def _track_to_played_track(self, track):
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

    def fetch_newest_played_tracks(self, last_imported_datetime):
        tracks = self.spotify.get_recently_played_tracks(after=last_imported_datetime)
        played_tracks = [self._track_to_played_track(track) for track in tracks]
        return played_tracks

    def fetch_stats(self):
        s = HoergewohnheitenStats(self.csv_file_path)
        return s.as_dict

    def git_push_files(self, file_paths=None):
        if file_paths:
            paths = [f for f in file_paths if os.path.exists(f)]
        else:
            paths = [f for f in [self.csv_file_path, self.json_file_path] if os.path.exists(f)]
        repo = Repo(settings.PATH_TO_DATA_REPO)
        repo.index.add(paths)
        repo.index.commit("Updating files.")
        repo.remote('origin').push()

    def write_tracks_to_csv(self, tracks):
        initial_write = False if os.path.exists(self.csv_file_path) else True
        with open(self.csv_file_path, 'a') as f:
            if initial_write:
                f.write("{}\n".format(CSV_HEADER))
            for track in reversed(tracks):  # Reverse tracks so latest play is at the bottom
                f.write("{}\n".format(track.csv_string))

    def write_stats_to_json(self, stats):
        with open(self.json_file_path, 'w') as f:
            json.dump(stats, f, sort_keys=True, indent=4)

    def process(self, last_imported_datetime):
        print("Fetching new played tracks.")
        tracks = self.fetch_newest_played_tracks(last_imported_datetime)
        print("{} tracks found.".format(len(tracks)))
        if tracks:
            print("Writing track(s) to file {}.".format(self.csv_file_path))
            self.write_tracks_to_csv(tracks)
            print("Fetching stats.")
            stats = self.fetch_stats()
            print("Writing stats to file {}.".format(self.json_file_path))
            self.write_stats_to_json(stats)
            print("Pushing file(s) to GitHub.")
            self.git_push_files()


if __name__ == '__main__':
    print("Starting run at {}".format(datetime.now()))

    # Get last imported datetime
    last_imported_datetime_as_utc = get_last_imported_datetime_as_utc()

    # Process
    mgr = HoergewohnheitenManager()
    mgr.process(last_imported_datetime=last_imported_datetime_as_utc)

    print("Bye.")
