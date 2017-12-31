import argparse
from datetime import datetime

import spotify_settings
import util

from connections import SpotifyConnection


class HoergewohnheitenManager(object):

    def __init__(self, spotify_user_data):
        self.spotify = SpotifyConnection(user_data=spotify_user_data)

    def process_hoergewohnheiten(self):
        self.spotify.extract_plays()


def process_hoergewohnheiten(user_name):
    print("***", user_name, "***")
    user_data = spotify_settings.SPOTIFY_USERS[user_name]
    mgr = HoergewohnheitenManager(user_data)
    mgr.process_hoergewohnheiten()


if __name__ == '__main__':
    print(util.LOG_HEADER)
    print("Script started at {}.".format(datetime.now()))

    # Argparse
    parser = argparse.ArgumentParser(description='Hoergewohnheiten')
    parser.add_argument('-u', dest='user_name')
    args = parser.parse_args()

    if args.user_name:
        process_hoergewohnheiten(args.user_name)
    else:
        for user_name in spotify_settings.SPOTIFY_USERS:
            process_hoergewohnheiten(user_name)

    print("Script finished at {}.".format(datetime.now()))
