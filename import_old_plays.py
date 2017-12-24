import argparse
from datetime import datetime
from glob import glob
import csv

import settings

from connections import SpotifyConnection


def import_old_plays(spotify_connection):
    print("* Loading csv files")
    for csv_file_path in glob('{}/[0-9][0-9][0-9][0-9]-[0-9][0-9].csv'.format(settings.PATH_TO_DATA_REPO)):
        print("* Working", csv_file_path)
        plays = []
        with open(csv_file_path, 'r') as csv_file:
            lines = csv.reader(csv_file, delimiter=',')
            for line_number, line in enumerate(lines, 1):
                if line_number == 1:
                    continue
                timestamp = int(line[0])
                played_at = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%dT%H:%M:%SZ')
                play = spotify_connection.get_play_from_played_at_utc_and_track_id(played_at, line[1])
                spotify_connection.db.save_instance(play)


if __name__ == '__main__':
    # Argparse
    parser = argparse.ArgumentParser(description='Hoergewohnheiten')
    parser.add_argument('-u', dest='user_name')
    args = parser.parse_args()

    spotify_connection = SpotifyConnection(settings.SPOTIFY_USERS[args.user_name])
    import_old_plays(spotify_connection)
