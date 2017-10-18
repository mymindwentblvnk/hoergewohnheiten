from dateutil import tz


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


def convert_datetime_utc_to_cet(datetime_to_convert, utc_to_cet=True):
    if utc_to_cet:
        from_tz = tz.gettz('UTC')
        to_tz = tz.gettz('CET')
    else:
        from_tz = tz.gettz('CET')
        to_tz = tz.gettz('UTC')

    datetime_to_convert = datetime_to_convert.replace(tzinfo=from_tz)
    converted_datetime = datetime_to_convert.astimezone(to_tz)
    return converted_datetime
