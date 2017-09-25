LOG_HEADER = '''
 _     ___   ____  ___   __    ____  _       ___   _     _      _     ____  _  _____  ____  _     
| |_| / / \ | |_  | |_) / /`_ | |_  \ \    // / \ | |_| | |\ | | |_| | |_  | |  | |  | |_  | |\ | 
|_| | \_\_/ |_|__ |_| \ \_\_/ |_|__  \_\/\/ \_\_/ |_| | |_| \| |_| | |_|__ |_|  |_|  |_|__ |_| \| 
'''

def pad_number(number):
    return "0{}".format(number)[-2:]


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]
