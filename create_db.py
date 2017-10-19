import util
from connections import SpotifyConnection
from models import SQLiteConnection
import settings
from glob import glob


def load_plays_from_csv_files():
    result = []

    csv_file_pattern = '{}/[0-9][0-9][0-9][0-9]-[0-9][0-9].csv'.format(settings.PATH_TO_DATA_REPO)
    for csv_file in sorted(glob(csv_file_pattern)):
        try:
            with open(csv_file, 'r') as f:
                for line in f.readlines():
                    line_array = line.split(',')
                    if line_array[0] == 'played_at_as_utc':
                        continue
                    played_at = '{}Z'.format(line_array[0]).replace(' ', 'T')
                    track_id = line_array[1]
                    result.append((played_at, track_id))
        except (FileNotFoundError, IndexError):
            pass
    return result

if __name__ == '__main__':

    plays =[]

    db = SQLiteConnection(settings.DB_PATH)
    # db.drop_db()
    # db.create_db()
    spotify = SpotifyConnection(db)

    print("Loading plays from CSV files.")
    play_tuples = load_plays_from_csv_files()

    for p in play_tuples:
        played_at_utc, track_id = p
        play = spotify._get_play_from_played_at_utc_and_track_id(played_at_utc, track_id)
        plays.append(play)

    db.save_instances(plays)
