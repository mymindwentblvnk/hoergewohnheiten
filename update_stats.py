from datetime import datetime
from main import HoergewohnheitenManager, HoergewohnheitenStats
from main import pad_number
from settings import PATH_TO_DATA_REPO


now = datetime.now()


def month_year_iterator(start_month, start_year, end_month, end_year):
    # See https://stackoverflow.com/questions/5734438/how-to-create-a-month-iterator
    year_month_start = 12 * start_year + start_month - 1
    year_month_end = 12 * end_year + end_month
    for year_month in range(year_month_start, year_month_end):
        year, month = divmod(year_month, 12)
        yield year, month + 1


def update_stats(year_start=2017, month_start=8):
    file_names = []

    for year, month in month_year_iterator(month_start, year_start, now.month, now.year):
        mgr = HoergewohnheitenManager(year=year, month=month)
        stats = mgr.fetch_stats()
        mgr.write_stats_to_json(stats)
        file_names.append('{}/{}-{}.json'.format(PATH_TO_DATA_REPO, year, pad_number(month)))

    HoergewohnheitenManager().git_push_files(file_names)

if __name__ == '__main__':
    update_stats()
