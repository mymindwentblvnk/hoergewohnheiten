from datetime import datetime
from dateutil.relativedelta import relativedelta

from api import Counts

# Create https://github.com/plamere/spotipy/blob/master/examples/create_playlist.py
# Add https://github.com/plamere/spotipy/blob/master/examples/add_tracks_to_playlist.py
# Get https://github.com/plamere/spotipy/blob/master/examples/user_playlists.py

NOW = datetime.now()
YEAR_PATTERN = "[{year}] {type}"
MONTH_PATTERN = "[{month} {year}] {type}"


def get_first_year_by_user_name(user_name):
    return datetime(2017, 11, 1)


def get_years_by_user_name(user_name):
    now = datetime(NOW.year, 1, 1)
    first_play_date = get_first_year_by_user_name(user_name).replace(month=1, day=1)
    temp = first_play_date

    while temp < now:
        yield temp, temp + relativedelta(years=1)
        temp += relativedelta(years=1)


def get_months_by_user_name(user_name):
    now = datetime(NOW.year, NOW.month, 1)
    first_play_date = get_first_year_by_user_name(user_name).replace(day=1)
    temp = first_play_date

    while temp < now:
        yield temp, temp + relativedelta(months=1)
        temp += relativedelta(months=1)


if __name__ == '__main__':
    api = Counts()
    user_name = 'rainertitan'

    # for y, next_y in get_years_by_user_name(user_name):
    #     print(y, next_y)
    #     year = y.strftime('%Y')
    #     month = y.strftime('%b')
    #     for t in ('Songs', 'Albums', 'Artists'):
    #         playlist_name = YEAR_PATTERN.format(type=t,
    #                                             user_name=user_name,
    #                                             year=year,
    #                                             month=month)
    #         print(playlist_name)  # Username in description

    for y, next_y in get_months_by_user_name(None):
        print(y, next_y)
        year = y.strftime('%y')
        month = y.strftime("%b")
        for t in ('Songs', 'Albums', 'Artists'):
            playlist_name = MONTH_PATTERN.format(type=t,
                                                user_name=user_name,
                                                year=year,
                                                month=month)
            print(playlist_name)  # Username in description
