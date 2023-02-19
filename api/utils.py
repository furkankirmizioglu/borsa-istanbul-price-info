from datetime import datetime

def parse_int(text):
    if len(text) > 0:
        return int(text.replace('.', ''))
    else:
        return 0


def today():
    return datetime.now().strftime('%Y%m%d')


def now():
    return datetime.now().strftime('%Y%m%d%H%M%S')