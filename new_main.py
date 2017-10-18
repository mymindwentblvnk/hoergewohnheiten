from datetime import datetime
import os
from glob import glob
import json

from git import Repo

import settings
import util

from connections import SpotifyConnection


CSV_HEADER = "played_at_as_utc,track_id"


class HoergewohnheitenManager(object):

    def __init__(self, year=None, month=None):
        self.year = year if year else datetime.now().year
        self.month = month if month else datetime.now().month

        self.spotify = SpotifyConnection()

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

    def process(self):
        print(util.LOG_HEADER)
        print("* Fetching last imported datetime")
        last_imported_datetime = self._get_last_imported_datetime_as_utc()
        print(last_imported_datetime)

        print("* Fetching new played tracks")
        tracks = self.fetch_newest_played_tracks(last_imported_datetime)
        print("> {} play(s) found".format(len(tracks)))
        pass


if __name__ == '__main__':
    mgr = HoergewohnheitenManager()
    mgr.process()
