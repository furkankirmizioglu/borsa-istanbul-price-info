from datetime import datetime

def parseInt(text):
    return int(text.replace('.', ''))


def today():
    return datetime.now().strftime('%Y%m%d')


def now():
    return datetime.now().strftime('%Y%m%d%H%M%S')