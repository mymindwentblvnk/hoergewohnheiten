from dateutil import tz
from datetime import datetime


LOG_HEADER = '''
 _     ___   ____  ___   __    ____  _       ___   _     _      _     ____  _  _____  ____  _
| |_| / / \ | |_  | |_) / /`_ | |_  \ \    // / \ | |_| | |\ | | |_| | |_  | |  | |  | |_  | |\ |
|_| | \_\_/ |_|__ |_| \ \_\_/ |_|__  \_\/\/ \_\_/ |_| | |_| \| |_| | |_|__ |_|  |_|  |_|__ |_| \|'''


def pad_number(number):
    return "0{}".format(number)[-2:]


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def convert_played_at_from_csv_to_datetime(played_at):
    try:
        return datetime.strptime(played_at, '%Y-%m-%d %H:%M:%S.%f')
    except:
        # For the single moment where the played at time hits a full second
        return datetime.strptime(played_at, '%Y-%m-%d %H:%M:%S')

def convert_datetime_from_timezone_to_timezone(datetime_to_convert, from_tz_code='UTC', to_tz_code='CET'):
    # TODO use pytz (https://stackoverflow.com/questions/4770297/python-convert-utc-datetime-string-to-local-datetime)
    from_tz = tz.gettz(from_tz_code)
    to_tz = tz.gettz(to_tz_code)

    datetime_to_convert = datetime_to_convert.replace(tzinfo=from_tz)
    converted_datetime = datetime_to_convert.astimezone(to_tz)
    return converted_datetime
