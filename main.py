from datetime import datetime, timedelta
import os
import glob
import json

from git import Repo

import settings
import util

from connections import OWMConnection, SpotifyConnection
from stats import HoergewohnheitenMonthStats


CSV_HEADER = "played_at_as_utc,track_id,track_name,track_bpm,track_energy,track_valence,artist_id,artist_name,artist_genres,album_id,album_name,album_label,album_genres,weather_temperature,weather_status"


def track_to_csv_string(track, weather_temperature, weather_status):
    fields = [track.played_at,
              track.track_id,
              track.track_name,
              track.audio_feature.tempo,
              track.audio_feature.energy,
              track.audio_feature.valence,
              track.artist.artist_id,
              track.artist.artist_name,
              track.artist.artist_genres,
              track.album.album_id,
              track.album.album_name,
              track.album.label,
              track.album.album_genres,
              weather_temperature,
              weather_status]
    escaped_fields = [str(field).replace(',', '').replace('\'', '').replace('\"', '') for field in fields]
    return ",".join(escaped_fields)


class HoergewohnheitenManager(object):

    def __init__(self, year=None, month=None):
        self.path_to_data_repo = settings.PATH_TO_DATA_REPO
        self.year = year if year else datetime.now().year
        self.month = month if month else datetime.now().month
        self.spotify = SpotifyConnection()
        self.weather = OWMConnection().get_weather()
        self.csv_file_path = '{}/{}-{}.csv'.format(self.path_to_data_repo,
                                                   self.year,
                                                   util.pad_number(self.month))
        self.json_file_path = '{}/{}-{}.json'.format(self.path_to_data_repo,
                                                     self.year,
                                                     util.pad_number(self.month))
        self.overview_json_file_path = '{}/overview.json'.format(settings.PATH_TO_DATA_REPO)


    def _convert_datetime_to_utc_in_ms(self, dt):
        neunzehnhundertsiebzig = datetime.utcfromtimestamp(0)
        return int((dt - neunzehnhundertsiebzig).total_seconds() * 1000)


    def _convert_played_at_from_csv_to_datetime(self, played_at):
        try:
            return datetime.strptime(played_at, '%Y-%m-%d %H:%M:%S.%f')
        except:
            # For the single moment where the played at time hits a full second
            return datetime.strptime(played_at, '%Y-%m-%d %H:%M:%S')

    def _get_last_imported_datetime_as_utc(self):

        csv_file_pattern = '{}/[0-9][0-9][0-9][0-9]-[0-9][0-9].csv'.format(self.path_to_data_repo)
        for csv_file in sorted(glob.glob(csv_file_pattern), reverse=True):
            try:
                with open(csv_file, 'r') as f:
                    lines = f.readlines()
                    last_line = lines[-1]
                    played_at = last_line.split(',')[0]
                    dt = self._convert_played_at_from_csv_to_datetime(played_at)
                    return self._convert_datetime_to_utc_in_ms(dt)
            except (FileNotFoundError, IndexError):
                pass

    def _stringify_lists(self, list_items):
        return "|".join(list_items) if list_items else ""

    def fetch_newest_played_tracks(self, last_imported_datetime):
        return self.spotify.get_recently_played_tracks(after=last_imported_datetime)

    def fetch_stats(self):
        s = HoergewohnheitenMonthStats(self.csv_file_path)
        return s.as_dict()

    def git_push_files(self, file_paths):
        paths = [f for f in file_paths if os.path.exists(f)]
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
                temperature = self.weather.temperature
                status = self.weather.status
                f.write("{}\n".format(track_to_csv_string(track,
                                                          self.weather.temperature,
                                                          self.weather.status)))

    def write_dictionary_to_json(self, dictionary, json_path):
        with open(json_path, 'w') as f:
            json.dump(dictionary, f, sort_keys=True, indent=4)

    def create_stats_overview(self):
        pattern_months = '{}/[0-9][0-9][0-9][0-9]-[0-9][0-9].json'.format(self.path_to_data_repo)
        pattern_years = '{}/[0-9][0-9][0-9][0-9].json'.format(self.path_to_data_repo)

        month_file_paths = glob.glob(pattern_months)
        year_file_paths = glob.glob(pattern_years)
        all_file_path = 'all_time.json' if os.path.exists('{}/all_time.json'.format(self.path_to_data_repo)) else None

        month_file_paths = [f.split('/')[-1] for f in month_file_paths]
        year_file_paths = [f.split('/')[-1] for f in year_file_paths]

        return {
            'months': month_file_paths,
            'years': year_file_paths,
            'all_time': all_file_path
        }

    def process(self):
        print("Fetching last imported datetime.")
        last_imported_datetime = self._get_last_imported_datetime_as_utc()

        print("Fetching new played tracks.")
        tracks = self.fetch_newest_played_tracks(last_imported_datetime)
        print("{} tracks found.".format(len(tracks)))

        if tracks:
            print("Writing track(s) to file {}.".format(self.csv_file_path))
            self.write_tracks_to_csv(tracks)

            print("Fetching stats.")
            stats = self.fetch_stats()
            print("Writing stats to file {}.".format(self.json_file_path))
            self.write_dictionary_to_json(stats, self.json_file_path)

            print("Create stats list.")
            stats_overview = self.create_stats_overview()
            print("Writing stats overview to file {}.".format(self.overview_json_file_path))
            self.write_dictionary_to_json(stats_overview, self.overview_json_file_path)

            print("Pushing file(s) to GitHub.")
            self.git_push_files([self.csv_file_path, self.json_file_path, self.overview_json_file_path])


if __name__ == '__main__':
    print("Starting run at {}".format(datetime.now()))

    mgr = HoergewohnheitenManager()
    mgr.process()

    print("Bye.")
