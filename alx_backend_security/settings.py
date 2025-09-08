from pathlib import Path
import os
from datetime import timedelta
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

# =======================
# SECURITY
# =======================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")  # Override in prod
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# =======================
# Applications
# =======================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Celery support
    'django_celery_results',
    'django_celery_beat',

    # Third-party
    "rest_framework",
    "drf_yasg",

    # Local apps
    "ip_tracking",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "ip_tracking.middleware.RequestLogMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "alx_backend_security.urls"

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

WSGI_APPLICATION = "alx_backend_security.wsgi.application"

# =======================
# Database
# - SQLite locally, Postgres in Render
# =======================
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

# =======================
# Password validation
# =======================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =======================
# Internationalization
# =======================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# =======================
# Static files
# =======================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # for Render collectstatic

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =======================
# Celery Configuration
# =======================
CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "amqps://qzdqfqce:wBHGVYY6IHo_xztUXhx97I_Ku5n-SOxs@rat.rmq2.cloudamqp.com/qzdqfqce"  # fallback CloudAMQP URL
)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "django-db")

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

# Celery Beat Schedule (DB scheduler)
CELERY_BEAT_SCHEDULE = {
    "detect-suspicious-activity-hourly": {
        "task": "ip_tracking.tasks.detect_suspicious_activity",
        "schedule": crontab(minute=0, hour="*"),  # every hour
    },
}

# =======================
# DRF Default settings
# =======================
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ]
}

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"