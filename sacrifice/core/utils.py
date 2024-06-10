import datetime


def year_choices(from_year=1989, additional_years=1):
    return [(r, r) for r in range(from_year, datetime.date.today().year + additional_years)]


def current_year():
    return datetime.date.today().year
