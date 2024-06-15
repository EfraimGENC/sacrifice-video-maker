import datetime
import random
import string
from typing import Union


def year_choices(from_year=1989, additional_years=1):
    return [(r, r) for r in range(from_year, datetime.date.today().year + additional_years)]


def current_year():
    return datetime.date.today().year


def get_safe_characters(remove: Union[list[str], tuple[str]] = ("I", "l", "O", "o", "0")):
    return ''.join(char for char in string.ascii_letters + string.digits if char not in remove)


def get_random_string(length, options='abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789'):
    options = options or get_safe_characters()
    return ''.join(random.choice(options) for _ in range(length))
