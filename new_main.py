from datetime import datetime
import os
from glob import glob
import json

from git import Repo

import settings
import util

from connections import SpotifyConnection
from stats import HoergewohnheitenMonthStats
from stats import HoergewohnheitenYearStats
from stats import HoergewohnheitenAllTimeStats


CSV_HEADER = "played_at_as_utc,track_id"


class HoergewohnheitenManager(object):

    def __init__(self, year=None, month=None):
        self.year = year if year else datetime.now().year
        self.month = month if month else datetime.now().month

        self.spotify = SpotifyConnection()

        self.overview_json_file_path = '{}/overview.json'.format(settings.PATH_TO_DATA_REPO)
        self.latest_plays_json_file_path = '{}/latest_plays.json'.format(settings.PATH_TO_DATA_REPO)
        self.latest_n_plays = 20

    def _get_last_imported_datetime_as_utc(self):
        csv_file_pattern = '{}/[0-9][0-9][0-9][0-9]-[0-9][0-9].csv'.format(settings.PATH_TO_DATA_REPO)
        for csv_file in sorted(glob(csv_file_pattern), reverse=True):
            try:
                with open(csv_file, 'r') as f:
                    lines = f.readlines()
                    last_line = lines[-1]
                    played_at = last_line.split(',')[0]
                    dt = util.convert_played_at_from_csv_to_datetime(played_at)
                    return util.convert_datetime_to_utc_in_ms(dt)
            except (FileNotFoundError, IndexError):
                pass

    def fetch_newest_played_tracks(self, last_imported_datetime):
        return self.spotify.get_plays(after=last_imported_datetime)

    def fetch_month_stats(self):
        s = HoergewohnheitenMonthStats(year=self.year, month=self.month)
        return s.as_dict()

    def fetch_year_stats(self):
        s = HoergewohnheitenYearStats(year=self.year)
        return s.as_dict()

    def fetch_all_time_stats(self):
        s = HoergewohnheitenAllTimeStats()
        return s.as_dict()

    def git_pull(self):
        repo = Repo(settings.PATH_TO_DATA_REPO)
        origin = repo.remotes.origin
        origin.pull()

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
                f.write("{}\n".format(track_to_csv_string(track,
                                                          self.weather.temperature,
                                                          self.weather.status)))

    def write_dictionary_to_json(self, dictionary, json_path):
        with open(json_path, 'w') as f:
            json.dump(dictionary, f, sort_keys=True, indent=4)

    def create_stats_overview(self):
        pattern_months = '{}/[0-9][0-9][0-9][0-9]-[0-9][0-9].json'.format(settings.PATH_TO_DATA_REPO)
        pattern_years = '{}/[0-9][0-9][0-9][0-9].json'.format(settings.PATH_TO_DATA_REPO)

        month_file_paths = glob(pattern_months)
        year_file_paths = glob(pattern_years)
        all_file_path = 'all_time.json' if os.path.exists('{}/all_time.json'.format(settings.PATH_TO_DATA_REPO)) else None

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

    def create_latest_plays_overview(self):
        csv_file_path = '{}/{}-{}.csv'.format(settings.PATH_TO_DATA_REPO,
                                              self.year,
                                              util.pad_number(self.month))
        result = {}
        with open(csv_file_path, 'r') as f:
            plays = f.readlines()
            for index, row in enumerate(reversed(plays[-self.latest_n_plays:]), 1):
                play = row.split(",")
                played_at_as_utc = play[0]
                track_id = play[1]
                track = self.spotify.get_track(track_id)
                result[index] = {}
                result[index]['played_at_as_utc'] = played_at_as_utc
                result[index]['id'] = track.track_id
                result[index]['name'] = track.track_name
                result[index]['spotify_url'] = track.track_url
                result[index]['artist'] = {}
                result[index]['artist']['id'] = track.artist.artist_id
                result[index]['artist']['name'] = track.artist.artist_name
                result[index]['artist']['image_url'] = track.artist.artist_picture_url
                result[index]['artist']['spotify_url'] = track.artist.artist_url
                result[index]['album'] = {}
                result[index]['album']['id'] = track.album.album_id
                result[index]['album']['name'] = track.album.album_name
                result[index]['album']['image_url'] = track.album.cover_url
                result[index]['album']['spotify_url'] = track.album.album_url
        return result

    def process_bak(self):
        print(util.LOG_HEADER)
        print("* Fetching last imported datetime")
        last_imported_datetime = self._get_last_imported_datetime_as_utc()

        print("* Fetching new played tracks")
        tracks = self.fetch_newest_played_tracks(last_imported_datetime)
        print("> {} play(s) found".format(len(tracks)))

        if tracks:
            print("* Git pull")
            self.git_pull()

            print("* Writing new plays to csv")
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

            print("* Create latest plays overview")
            latest_plays_overview = self.create_latest_plays_overview()
            self.write_dictionary_to_json(latest_plays_overview, self.latest_plays_json_file_path)

            print("* Create stats overview")
            stats_overview = self.create_stats_overview()
            self.write_dictionary_to_json(stats_overview, self.overview_json_file_path)

            print("* Git push")
            self.git_push_files()

    def process(self):
        print(util.LOG_HEADER)
        print("* Fetching last imported datetime")
        last_imported_datetime = self._get_last_imported_datetime_as_utc()

        print("* Fetching new played tracks")
        tracks = self.fetch_newest_played_tracks(last_imported_datetime)
        print("> {} play(s) found".format(len(tracks)))
        pass


if __name__ == '__main__':
    mgr = HoergewohnheitenManager()
    mgr.process()
