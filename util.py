from dateutil import tz
from datetime import datetime

from glob import glob

import settings


LOG_HEADER = '''
 _     ___   ____  ___   __    ____  _       ___   _     _      _     ____  _  _____  ____  _
| |_| / / \ | |_  | |_) / /`_ | |_  \ \    // / \ | |_| | |\ | | |_| | |_  | |  | |  | |_  | |\ |
|_| | \_\_/ |_|__ |_| \ \_\_/ |_|__  \_\/\/ \_\_/ |_| | |_| \| |_| | |_|__ |_|  |_|  |_|__ |_| \|
'''


def set_timezone_to_datetime(datetime_to_set, timezone):
    return datetime_to_set.replace(tzinfo=tz.gettz(timezone))


def convert_played_at_from_response_to_datetime(played_at):
    try:
        return datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        # For the single moment where the played at time hits a full second
        return datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%SZ')


def convert_datetime_from_timezone_to_timezone(datetime_to_convert,
                                               from_tz_code='UTC',
                                               to_tz_code=settings.TARGET_TIMEZONE):
    from_tz = tz.gettz(from_tz_code)
    to_tz = tz.gettz(to_tz_code)

    datetime_to_convert = datetime_to_convert.replace(tzinfo=from_tz)
    converted_datetime = datetime_to_convert.astimezone(to_tz)
    return converted_datetime
