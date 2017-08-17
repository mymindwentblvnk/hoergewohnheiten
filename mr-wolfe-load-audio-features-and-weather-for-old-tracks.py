from main import HoergewohnheitenManager
from main import convert_played_at_to_datetime

import pickle
import csv


OLD_INDEX_PLAYED_AT = 0
OLD_INDEX_TRACK_ID = 1
OLD_INDEX_TRACK_NAME = 2
OLD_INDEX_ARTIST_ID = 3
OLD_INDEX_ARTIST_NAME = 4
OLD_INDEX_ALBUM_ID = 5
OLD_INDEX_ALBUM_NAME = 6


def expand_old_row_to_new_row(row):
    # Cannot get weather from the past
    weather_temperature = ''
    weather_status = ''

    track_id = row[OLD_INDEX_TRACK_ID]
    album_id = row[OLD_INDEX_ALBUM_ID]

    mgr = HoergewohnheitenManager()
    f = mgr.get_audio_feature(track_id)
    a = mgr.get_album(album_id)

    return [row[OLD_INDEX_PLAYED_AT], 
            row[OLD_INDEX_TRACK_ID],
            row[OLD_INDEX_TRACK_NAME],
            str(f['tempo']),
            str(f['energy']),
            row[OLD_INDEX_ARTIST_ID],
            row[OLD_INDEX_ARTIST_NAME],
            row[OLD_INDEX_ALBUM_ID],
            row[OLD_INDEX_ALBUM_NAME],
            a['label'].replace(',', ''),
            mgr._stringify_genres(a['genres']),
            weather_temperature,
            weather_status]


def main():
    header = 'played_at,track_id,track_name,track_bpm,track_energy,artist_id,artist_name,album_id,album_name,album_label,album_genres,weather_temperature,weather_status'
    try:
        d = pickle.load(open('mr-wolfe.pckl', 'rb'))
    except:
        d = {}
        with open('/home/michael-123/src/HoergewohnheitenData/2017-08.csv', 'r') as csv_file:
            rows = csv.reader(csv_file, delimiter=',')
            csv_length = 904
            for index, row in enumerate(rows):
                print("Processing track {} {}/{}.".format(row[OLD_INDEX_TRACK_ID], index + 1, csv_length))
                if index == 0:
                    continue
                try:
                    dt = convert_played_at_to_datetime(row[0], date_format='%Y-%m-%d %H:%M:%S')
                except ValueError:
                    dt = convert_played_at_to_datetime(row[0], date_format='%Y-%m-%d %H:%M:%S.%f')
                d[dt] = expand_old_row_to_new_row(row)

    keys = d.keys()
    ordered_keys = sorted(keys)

    pickle.dump(d, open('mr-wolfe.pckl', 'wb'))

    with open('out.csv', 'w') as f:
        f.write("{}\n".format(header))
        for key in ordered_keys:
            f.write("{}\n".format(",".join(d[key])))


if __name__ == '__main__':
    main()
