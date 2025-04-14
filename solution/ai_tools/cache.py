from django.core.cache import cache


def enable_moderation():
    cache.set("moderation", value=True, timeout=None)


def disable_moderation():
    cache.set("moderation", value=False, timeout=None)


def get_moderation_mode() -> bool:
    return cache.get("moderation", default=False)
