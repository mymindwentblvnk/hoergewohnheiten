from datetime import datetime

from main import HoergewohnheitenManager
import util

import settings


now = datetime.now()


def month_year_iterator(start_month, start_year, end_month, end_year):
    # See https://stackoverflow.com/questions/5734438/how-to-create-a-month-iterator
    year_month_start = 12 * start_year + start_month - 1
    year_month_end = 12 * end_year + end_month
    for year_month in range(year_month_start, year_month_end):
        year, month = divmod(year_month, 12)
        yield year, month + 1


def update_stats(year_start=2017, month_start=8):
    print(util.LOG_HEADER)
    print("* Updating month stats")
    for year, month in month_year_iterator(month_start, year_start, now.month, now.year):
        print("> {}-{}".format(year, util.pad_number(month)))

        mgr = HoergewohnheitenManager(year=year, month=month)
        stats = mgr.fetch_month_stats()
        json_file_path = '{}/{}-{}.json'.format(settings.PATH_TO_DATA_REPO, year, util.pad_number(month))
        mgr.write_dictionary_to_json(stats, json_file_path)

    print("* Updating year stats")
    for year in range(year_start, now.year + 1):
        print("> {}".format(year))
        mgr = HoergewohnheitenManager(year=year)
        stats = mgr.fetch_year_stats()
        json_file_path = '{}/{}.json'.format(settings.PATH_TO_DATA_REPO, year)
        mgr.write_dictionary_to_json(stats, json_file_path)

    print("* Updating all time stats")
    mgr = HoergewohnheitenManager()
    stats = mgr.fetch_all_time_stats()
    json_file_path = '{}/all_time.json'.format(settings.PATH_TO_DATA_REPO, year)
    mgr.write_dictionary_to_json(stats, json_file_path)

    # For all new files
    print("* Git pull")
    mgr.git_pull()
    print("* Git push")
    mgr.git_push_files()


if __name__ == '__main__':
    update_stats()
