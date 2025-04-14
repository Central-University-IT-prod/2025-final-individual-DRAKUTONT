from django.core.cache import cache


def set_date(date: int):
    cache.set("current_date", date, timeout=None)


def get_date() -> int:
    return cache.get("current_date", default=0)
