from datetime import datetime
import os
from glob import glob
import json

from git import Repo

import settings
import util

from connections import SpotifyConnection
from models import SQLiteConnection, Play


class GithubPullPushMixin(object):

    def git_pull(self):
        repo = Repo(settings.PATH_TO_DATA_REPO)
        origin = repo.remotes.origin
        origin.pull()

    def git_push(self, extensions=('csv', 'json', 'sqlite')):
        files = []
        for extension in extensions:
            found_files = glob('{}/*.{}'.format(settings.PATH_TO_DATA_REPO, extension))
            files.extend(found_files)
        repo = Repo(settings.PATH_TO_DATA_REPO)
        repo.index.add(files)
        repo.index.commit("Updating files.")
        repo.remote('origin').push()


class HoergewohnheitenManager(GithubPullPushMixin):

    def __init__(self, year=None, month=None):
        self.year = year if year else datetime.now().year
        self.month = month if month else datetime.now().month

        self.db = SQLiteConnection(settings.DB_PATH)
        self.spotify = SpotifyConnection(db_connection=self.db)

    def write_plays_to_csv(self, plays):
        csv_file_path = '{}/{}-{}.csv'.format(settings.PATH_TO_DATA_REPO,
                                              self.year,
                                              util.pad_number(self.month))
        initial_write = False if os.path.exists(csv_file_path) else True
        with open(csv_file_path, 'a') as f:
            if initial_write:
                f.write("{}\n".format(settings.CSV_HEADER))
            for play in reversed(plays):  # Reverse tracks so latest play is at the bottom
                played_at = int(play.played_at_utc_timestamp)
                assert played_at == play.played_at_utc_timestamp  # Check if casting did no good
                f.write("{},{}\n".format(played_at, play.track.track_id))

    def get_latest_plays(self, latest_played_at):
        play_tuples = self.spotify.get_plays(after=latest_played_at)

        plays = []
        for played_at, track_id in play_tuples:
            play = self.spotify.get_play_from_played_at_utc_and_track_id(played_at, track_id)
            plays.append(play)
        return plays

    def process(self):
        print(util.LOG_HEADER)
        print("* Fetching latest played at")
        latest_played_at_utc_timestamp = self.db.latest_played_at_utc_timestamp
        print("Latest play: {}".format(latest_played_at_utc_timestamp))

        print("* Fetching new played tracks")
        plays = self.get_latest_plays(latest_played_at_utc_timestamp)
        print("> {} play(s) found".format(len(plays)))

        if plays:
            print("* Git pull")
            # self.git_pull()

            print("* Saving plays to CSV file")
            self.write_plays_to_csv(plays)

            print("* Saving plays to database")
            self.db.save_instances(plays)

            print("* Git push")
            # self.git_push()

if __name__ == '__main__':
    mgr = HoergewohnheitenManager()
    mgr.process()
