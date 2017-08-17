import csv
from main import convert_played_at_to_datetime


def main():
    d = {}
    header = None

    with open('../HoergewohnheitenData/2017-08.csv', 'r') as csv_file:
        rows = csv.reader(csv_file, delimiter=',')
        for index, row in enumerate(rows):
            if index == 0:
                header = row
                continue
            try:
                dt = convert_played_at_to_datetime(row[0], date_format='%Y-%m-%d %H:%M:%S')
            except ValueError:
                dt = convert_played_at_to_datetime(row[0], date_format='%Y-%m-%d %H:%M:%S.%f')
            d[dt] = row

    keys = d.keys()
    ordered_keys = sorted(keys)

    with open('../HoergewohnheitenData/out.csv', 'w') as f:
        f.write("{}\n".format(",".join(header)))
        for key in ordered_keys:
            f.write("{}\n".format(",".join(d[key])))
        

if __name__ == '__main__':
    main()
