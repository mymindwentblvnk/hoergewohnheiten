import csv
from glob import glob

import settings
import util


if __name__ == '__main__':
    csv_file_paths = glob('{}/[0-9][0-9][0-9][0-9]-[0-9][0-9].csv'.format(settings.PATH_TO_DATA_REPO))
    for csv_file_path in csv_file_paths:

        with open(csv_file_path, 'r') as csv_file:
            lines = csv.reader(csv_file, delimiter=',')

            with open('{}.NEW'.format(csv_file_path), 'w') as new_csv_file:
                for line_number, line in enumerate(lines, 1):

                    if line_number == 1:
                        new_csv_file.write('{}\n'.format(settings.CSV_HEADER))
                        continue

                    played_at_string, track_id = line[0], line[1]
                    d1 = util.convert_played_at_from_csv_to_datetime(played_at_string)
                    d2 = util.set_timezone_to_datetime(d1, 'UTC')

                    assert d2.timestamp() * 1000 == int(d2.timestamp() * 1000)
                    played_at_utc_timestamp = int(d2.timestamp() * 1000)

                    new_csv_file.write('{},{}\n'.format(played_at_utc_timestamp, line[1]))
