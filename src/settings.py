# Django settings for nih project.

import os, sys
from utils import site_path
from db_settings import db

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# FIXME: Use settings from db
COUCHDB_DATABASES = (
    ("jukebox.jukebox", "http://127.0.0.1:5984/jukebox"),
)

# FIXME: Test CouchDB
#import sys
#if 'test' in sys.argv or 'test_coverage' in sys.argv: #Covers regular testing and django-coverage
#    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
#    DATABASES['default']['NAME'] = site_path('default.db')
#    DATABASES['default']['TEST'] = {'NAME' : site_path('test.db')}
#    DATABASES['default']['OPTIONS'] = {'timeout': 20}

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
NOSE_ARGS = ["--with-coverage", "--cover-package=jukebox, simple_player", "--cover-html", "--cover-html-dir=coverage", "--with-xunit"]

LASTFM_USER="test_erlang"
LASTFM_PASSWORD="test_erlang"
LASTFM_ENABLED=False

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.sessions',
    'jsonrpc',
    'django_nose',
    'couchdbkit.ext.django',
    'jukebox'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            #'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            #'filters': ['require_debug_true'],
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'handlers': ['console'],
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
        },
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['console']
        # },
        'django.db.backends.schema': {
             'handlers': ['null']
        },
        'jukebox': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'handlers': ['console']
        },
        'jukebox.rpc': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'jukebox.tests': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'simple_player': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
}
