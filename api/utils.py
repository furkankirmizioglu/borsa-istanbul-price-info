from datetime import datetime


def parse_int(text):
    try:
        if len(text) > 0:
            value = int(text.replace('.', ''))
            return value
        else:
            return 0
    except ValueError as ex:
        print(ex)
        return 0


def today():
    return datetime.now().strftime('%Y%m%d')


def now():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def suggestion(score):
    if score >= 80:
        return "Güçlü Al"
    elif 70 <= score < 80:
        return "Al"
    elif 50 <= score < 70:
        return "Nötr"
    else:
        return "Sat"
