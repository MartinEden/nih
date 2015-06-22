# Django settings for nih project.

import os
from utils import site_path
from db_settings import db

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    'OPTIONS' : {
        'read_default_file': site_path('my.cnf'),
    },
        'NAME': db.name,                 # Or path to database file if using sqlite3.
        'USER': db.user,                 # Not used with sqlite3.
        'PASSWORD': db.password,         # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-uk'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n2(f@ymezbww2z4z1igrucfu(ngr*8rr5qt%v6v$ei$)(1lmmq'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

GENSHI_TEMPLATE_LOADERS = (
    'django_genshi.loaders.filesystem.load_template',
    'django_genshi.loaders.app_directories.load_template',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

CACHE_FOLDER = "/tmp/nih-cache"

TEMPLATE_DIRS = (
    site_path('jukebox/templates'),
)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_URL = 'https://github.com/lshift/nih/'

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.contrib.messages.context_processors.messages",
"django.core.context_processors.request"
)

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
NOSE_ARGS = ["--with-coverage", "--cover-package=nih.jukebox, simple_player", "--cover-html", "--cover-html-dir=coverage"]

LASTFM_USER="test_erlang"
LASTFM_PASSWORD="test_erlang"
LASTFM_ENABLED=False

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.contenttypes', # only here for the admin
    'jsonrpc',
    'django_nose',
    'jukebox'
)
