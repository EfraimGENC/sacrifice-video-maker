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


def generate_animal_video_path(prefix):
    def animal_video_path(instance, filename):
        random_string = get_random_string(8)
        path = 'animals/{season_year}_{season_id}/{animal_code}/{prefix}_{rnd}.{extension}'.format(
            season_year=instance.season.year,
            season_id=instance.season.id,
            animal_code=instance.code,
            prefix=prefix,
            rnd=random_string,
            extension=filename.split('.')[-1]
        )
        return path
    return animal_video_path


def animal_video_path_original(instance, filename):
    return generate_animal_video_path('original')(instance, filename)


def animal_video_path_processed(instance, filename):
    return generate_animal_video_path('processed')(instance, filename)


def animal_video_path_cover(instance, filename):
    return generate_animal_video_path('cover')(instance, filename)
