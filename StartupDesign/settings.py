"""
Django settings for StartupDesign project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv





SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-change-this-in-production"
)

DEBUG = True

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost,startupdesign.liara.run"
).split(",")



BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


GAPGPT_API_BASE = os.getenv("GAPGPT_API_BASE", "https://api.gapgpt.app/v1")
GAPGPT_API_KEY = os.getenv("GAPGPT_API_KEY", "")
GAPGPT_MODEL_NAME = os.getenv("GAPGPT_MODEL_NAME", "gapgpt-qwen-3.5")
GAPGPT_TIMEOUT = int(os.getenv("GAPGPT_TIMEOUT", "45"))


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "roadmap",
    "core",
    "nested_admin",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "StartupDesign.urls"
WSGI_APPLICATION = "StartupDesign.wsgi.application"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# =========================================================
# Database Liara
# =========================================================
""" 
DB_DIR = Path(os.getenv("SQLITE_DIR", "/usr/src/app/database"))
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "db.sqlite3"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DB_PATH),
    }
} 
 """
# =========================================================
# Database local
# =========================================================

if os.getenv("LIARA"):
    DB_DIR = Path("/usr/src/app/database")
    DB_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH = DB_DIR / "db.sqlite3"
else:
    DB_PATH = BASE_DIR / "db.sqlite3"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DB_PATH),
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"

# این پوشه برای فایل‌هایی است که خودتان می‌سازید (مثل CSSهای خودتان)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# این پوشه فقط برای زمان دپلوی (collectstatic) است
STATIC_ROOT = BASE_DIR / "staticfiles"



MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:edit_profile"
LOGOUT_REDIRECT_URL = "accounts:login"
