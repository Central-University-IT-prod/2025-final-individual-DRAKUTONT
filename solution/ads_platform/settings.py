import logging
from pathlib import Path

import environ
from dj_database_url import parse

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="secret")
DEBUG = env("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env(
    "DJANGO_ALLOWED_HOSTS",
    list,
    default=["*"],
)

SERVER_ADDRESS = env("SERVER_ADDRESS", default="REDACTED:8080")
SERVER_PORT = env("SERVER_PORT", default="8080")

REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_PORT = env("REDIS_PORT", default="6379")

POSTGRES_CONN = env("POSTGRES_CONN")

YANDEX_GPT_MODEL_TYPE = env("YANDEX_GPT_MODEL_TYPE")
YANDEX_GPT_CATALOG_ID = env("YANDEX_GPT_CATALOG_ID")
YANDEX_GPT_API_KEY = env("YANDEX_GPT_API_KEY")

MODERATION_PROMT = (
    "Ты модератор рекламной платформы. Распознавай мат и запрещенные темы"
    "в рекламных объявлениях(нелегальная деятельность, дискриминация,"
    "мошенничество, экстремизм, насилие и прочие). Если текст не прошел"
    "модерацию, необходимо вернуть причину. Если текст прошел модерацию,"
    "то необходимо вернуть 'Текст прошел валидацию'."
    "Тебе нельзя возвращать что-то иное, кроме этих значений."
)

GENERATION_PROMT = (
    "Ты — профессиональный маркетолог с опытом написания высококонверсионной "
    "рекламы. Для генерации рекламного текста ты изучаешь потенциальную "
    "целевую аудиторию, оптимизируешь рекламный текст так, чтобы он обращался "
    "именно к этой целевой аудитории. Напиши рекламный текст для следующих "
    "продуктов/услуг. Создай текст объявления с привлекающим внимание "
    "заголовком и убедительным призывом к действию, который побуждает "
    "пользователей к целевому действию. Не используй markdown "
    "форматирование и переносы строк."
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_prometheus",
    "minio_storage",
    # apps
    "ads.apps.AdsConfig",
    "advertisers.apps.AdvertisersConfig",
    "ai_tools.apps.AiToolsConfig",
    "clients.apps.ClientsConfig",
    "score.apps.ScoreConfig",
    "stats.apps.StatsConfig",
    "time_emulation.apps.TimeEmulationConfig",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "ads_platform.urls"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ads_platform.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {
            "client_encoding": "UTF8",
        },
        **parse(POSTGRES_CONN),
    },
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "NumericPasswordValidator",
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "ads_platform.custom": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

STORAGES = {
    "default": {
        "BACKEND": "minio_storage.storage.MinioMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

NINJA_PAGINATION_PER_PAGE = 10

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = False


STATIC_URL = "/static/"
STATIC_ROOT = "./static_files/"

MINIO_STORAGE_ENDPOINT = env(
    "MINIO_STORAGE_ENDPOINT",
    default="localhost:9000",
)
MINIO_STORAGE_ACCESS_KEY = "minioadmin"
MINIO_STORAGE_SECRET_KEY = "minioadmin"  # noqa: S105
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_OBJECT_METADATA = {"Cache-Control": "max-age=1000"}
MINIO_STORAGE_MEDIA_BUCKET_NAME = "media"
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_MEDIA_BACKUP_BUCKET = "Recycle Bin"
MINIO_STORAGE_MEDIA_BACKUP_FORMAT = "%c/"
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = False
MINIO_STORAGE_MEDIA_URL = "localhost:9000/media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
