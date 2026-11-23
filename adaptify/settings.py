"""
Django settings for the Adaptify API.

Everything environment-specific is read from environment variables (or a local
.env file) and has a default that works for local development.
"""

from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlparse

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# Set SECRET_KEY in the environment for any real deployment; this default is for local use only.
SECRET_KEY = config('SECRET_KEY', default='django-insecure-vu8hm7m!!46*7&68+m1qu38i@(mo7ut^@7)(y%6zp!)ztek$h&')

DEBUG = config('DEBUG', default=False, cast=bool)

# Extra hosts and frontend origins for a deployment come from the environment,
# as comma-separated lists.
ALLOWED_HOSTS = ["localhost", "127.0.0.1"] + config('ALLOWED_HOSTS', default='', cast=Csv())
# Render sets this to the service's public hostname.
if config('RENDER_EXTERNAL_HOSTNAME', default=''):
    ALLOWED_HOSTS.append(config('RENDER_EXTERNAL_HOSTNAME'))

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
] + config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'adaptify.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'adaptify.wsgi.application'

# Database: DATABASE_URL (postgres://user:password@host:port/name?options) takes
# priority, then the separate SUPABASE_DB_* values, then a local SQLite file.
DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL:
    url = urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': unquote(url.path.lstrip('/')),
            'USER': unquote(url.username or ''),
            'PASSWORD': unquote(url.password or ''),
            'HOST': url.hostname or '',
            'PORT': url.port or 5432,
            'OPTIONS': dict(parse_qsl(url.query)),
        }
    }
elif config('SUPABASE_DB_HOST', default=''):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('SUPABASE_DB_NAME'),
            'USER': config('SUPABASE_DB_USER'),
            'PASSWORD': config('SUPABASE_DB_PASSWORD'),
            'HOST': config('SUPABASE_DB_HOST'),
            'PORT': config('SUPABASE_DB_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
