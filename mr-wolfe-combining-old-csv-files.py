import os
import csv

import settings

from main import write_songs_to_csv
from main import git_push_csv
from main import convert_played_at_to_datetime 
from main import SpotifyConnection
from main import Song


class TrackCache(object):

    def __init__(self):
        self.spotify = SpotifyConnection(scope='user-read-recently-played')
        self.cache = {}

    def get_album_id_and_name_from_track_id(self, track_id):
        if track_id in self.cache:
            track_dict = self.cache[track_id]
        else:
            track_dict = self.spotify.client.track(track_id)
            self.cache[track_id] = track_dict
        return (track_dict['album']['id'], track_dict['album']['name'])


def main():
    cache = TrackCache()
    csv_directory = settings.PATH_TO_DATA_REPO

    all_tracks_dict = {}
    file_names = os.listdir(csv_directory)
    print("Processing {} files.".format(len(file_names)))

    for index, file_name in enumerate(file_names):
        print("{}/{} ({})".format(index + 1, len(file_names), file_name))

        if file_name.endswith('.csv'):
            with open('{}/{}'.format(csv_directory, file_name), 'r') as csv_file:
                rows_of_file = csv.reader(csv_file, delimiter=',')
                for row in rows_of_file:
                    if 'Played_At' in row or 'played_at' in row:
                        continue  # Skip header
                    try:
                        # Old csv
                        played_at = convert_played_at_to_datetime(row[1], date_format='%Y-%m-%d %H:%M:%S.%f')
                        (album_id, album_name) = cache.get_album_id_and_name_from_track_id(row[0])
                        song = Song(played_at=row[1],
                                    track_id=row[0],
                                    track_name = row[4],
                                    artist_id=row[2],
                                    artist_name=row[3],
                                    album_id=album_id,
                                    album_name=album_name)
                        all_tracks_dict[row[1]] = song
                    except:
                        # New csv
                        played_at = convert_played_at_to_datetime(row[0], date_format='%Y-%m-%d %H:%M:%S.%f')
                        song = Song(played_at=row[0],
                                    track_id=row[2],
                                    track_name = row[1],
                                    artist_id=row[3],
                                    artist_name=row[4],
                                    album_id=row[5],
                                    album_name=row[6])
                        all_tracks_dict[row[0]] = song

    # Order tracks by played_at
    songs = list(all_tracks_dict.values())
    ordered_songs = sorted(songs, 
                           key=lambda x: convert_played_at_to_datetime(x.played_at, date_format='%Y-%m-%d %H:%M:%S.%f'),
                           reverse=True)
    write_songs_to_csv(ordered_songs, '{}/combined.csv'.format(csv_directory))


if __name__ == '__main__':
    main()
