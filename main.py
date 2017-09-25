from datetime import datetime, timedelta
import os
from glob import glob
import json

from git import Repo

import settings
import util

from connections import OWMConnection, SpotifyConnection
from stats import HoergewohnheitenMonthStats
from stats import HoergewohnheitenYearStats
from stats import HoergewohnheitenAllTimeStats


CSV_HEADER = "played_at_as_utc,track_id,track_name,track_bpm,track_energy,track_valence,artist_id,artist_name,artist_genres,album_id,album_name,album_label,album_genres,weather_temperature,weather_status"


def stringify_lists(list_items):
    return "|".join(list_items) if list_items else ""


def track_to_csv_string(track, weather_temperature, weather_status):
    fields = [track.played_at,
              track.track_id,
              track.track_name,
              track.audio_feature.tempo,
              track.audio_feature.energy,
              track.audio_feature.valence,
              track.artist.artist_id,
              track.artist.artist_name,
              track.album.album_id,
              track.album.album_name,
              stringify_lists(track.album.album_genres),
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
        for csv_file in sorted(glob(csv_file_pattern), reverse=True):
            try:
                with open(csv_file, 'r') as f:
                    lines = f.readlines()
                    last_line = lines[-1]
                    played_at = last_line.split(',')[0]
                    dt = self._convert_played_at_from_csv_to_datetime(played_at)
                    return self._convert_datetime_to_utc_in_ms(dt)
            except (FileNotFoundError, IndexError):
                pass

    def fetch_newest_played_tracks(self, last_imported_datetime):
        return self.spotify.get_recently_played_tracks(after=last_imported_datetime)

    def fetch_month_stats(self):
        s = HoergewohnheitenMonthStats(year=self.year, month=self.month)
        return s.as_dict()

    def fetch_year_stats(self):
        s = HoergewohnheitenYearStats(year=self.year)
        return s.as_dict()

    def fetch_all_time_stats(self):
        s = HoergewohnheitenAllTimeStats()
        return s.as_dict()

    def git_push_files(self):
        paths = []
        for extension in ('csv', 'json'):
            found_files = glob('{}/*.{}'.format(settings.PATH_TO_DATA_REPO, extension))
            paths.extend(found_files)
        repo = Repo(settings.PATH_TO_DATA_REPO)
        repo.index.add(paths)
        repo.index.commit("Updating files.")
        repo.remote('origin').push()

    def write_tracks_to_csv(self, tracks):
        csv_file_path = '{}/{}-{}.csv'.format(settings.PATH_TO_DATA_REPO,
                                              self.year,
                                              util.pad_number(self.month))
        initial_write = False if os.path.exists(csv_file_path) else True
        with open(csv_file_path, 'a') as f:
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

        month_file_paths = glob(pattern_months)
        year_file_paths = glob(pattern_years)
        all_file_path = 'all_time.json' if os.path.exists('{}/all_time.json'.format(self.path_to_data_repo)) else None

        month_file_paths = [f.split('/')[-1] for f in month_file_paths]
        year_file_paths = [f.split('/')[-1] for f in year_file_paths]

        return {
            'months': month_file_paths,
            'years': year_file_paths,
            'all_time': all_file_path
        }

    def _get_json_file_path(self, year=None, month=None):
        if year and month:
            result = '{}/{}-{}.json'.format(settings.PATH_TO_DATA_REPO,
                                          year,
                                          util.pad_number(month))
        elif year and not month:
            result = '{}/{}.json'.format(settings.PATH_TO_DATA_REPO, year)
        elif not year and not month:
            result = '{}/all_time.json'.format(settings.PATH_TO_DATA_REPO)
        return result

    def process(self):
        print(util.LOG_HEADER)
        print("* Fetching last imported datetime")
        last_imported_datetime = self._get_last_imported_datetime_as_utc()

        print("* Fetching new played tracks")
        tracks = self.fetch_newest_played_tracks(last_imported_datetime)
        print("> {} track(s) found".format(len(tracks)))

        if tracks:
            print("* Writing new played track(s) to csv")
            self.write_tracks_to_csv(tracks)

            print("* Fetching stats")
            print("> Month")
            month_stats = self.fetch_month_stats()
            out_path = self._get_json_file_path(year=self.year, month=self.month)
            self.write_dictionary_to_json(month_stats, out_path)

            print("> Year")
            year_stats = self.fetch_year_stats()
            out_path = self._get_json_file_path(year=self.year)
            self.write_dictionary_to_json(year_stats, out_path)

            print("> All Time")
            all_time_stats = self.fetch_all_time_stats()
            out_path = self._get_json_file_path()
            self.write_dictionary_to_json(all_time_stats, out_path)

            print("* Create stats overview")
            stats_overview = self.create_stats_overview()
            self.write_dictionary_to_json(stats_overview, self.overview_json_file_path)

            print("* Pushing file(s) to GitHub")
            self.git_push_files()


if __name__ == '__main__':
    mgr = HoergewohnheitenManager()
    mgr.process()
