# Django settings for service_info project.
import os
from django.utils.translation import ugettext_lazy as _
from celery.schedules import crontab

# BASE_DIR = path/to/source/service_info
# E.g. this file is BASE_DIR/settings/base.py
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# PROJECT_ROOT = path/to/source
# This file is PROJECT_ROOT/service_info/settings/base.py
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TEAM_EMAIL = 'servicemap-team@caktusgroup.com'
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('Caktus IRC Service Info Team', TEAM_EMAIL),
)
SERVER_EMAIL = TEAM_EMAIL
DEFAULT_FROM_EMAIL = TEAM_EMAIL

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'service_info',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Beirut'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
    ('fr', _('French')),
]

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
# And that's what we want, otherwise we have no control.
USE_L10N = False
# Time display format:
TIME_FORMAT = "G:i"  # 24-hour time without leading zero; minutes
# Time input format(s):
TIME_INPUT_FORMATS = ('%H:%M',)  # 24-hour time, with leading zero; minutes

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'public', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public', 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/app/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    os.path.join(PROJECT_ROOT, 'frontend'),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'hfyyf*=)1!1m16vo$y=g8(r&po3(qvasinv&lv2i&%ztsg7y&a'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'service_info.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'service_info.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

INSTALLED_APPS = (
    # Our apps - Must precede django.contrib.auth so templates override Django's.
    'services',
    'email_user',
    # contenttypes needs to be listed before auth due to problems with
    # create_permissions and the TransactionTestCase/LiveServerTestCase
    # See https://code.djangoproject.com/ticket/10827
    # ¯\_(ツ)_/¯
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.gis',
    # External apps
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'basic': {
            'format': '%(asctime)s %(name)-20s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'basic',
            'filename': os.path.join(PROJECT_ROOT, 'service_info.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10,
        },
    },
    'root': {
        'handlers': ['file', 'mail_admins'],
        'level': 'INFO',
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'service_info': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# Application settings
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
    # Use Django's standard `django.contrib.auth` permissions
    # by default.  (We'll alter this as needed on a few specific
    # views.)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.auth.ServiceInfoTokenAuthentication',
    ),
    'PAGINATE_BY': None,
}


AUTH_USER_MODEL = 'email_user.EmailUser'

# Just use admin login view for now
LOGIN_URL = 'admin:login'


# How many days a new user has to activate their account
# by following the link in their new account email message.
ACCOUNT_ACTIVATION_DAYS = 3

# When someone successfully activates their user account,
# redirect them to this URL.
ACCOUNT_ACTIVATION_REDIRECT_URL = '/nosuchurl'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
    'serviceinfoauthorization',
)

STAGING_SITE_ID = 2
PRODUCTION_SITE_ID = 3
DEV_SITE_ID = 4

# If this changes here, also change the password fields'
# minlength attribute in frontend/templates/provider-form.hbs
MINIMUM_PASSWORD_LENGTH = 6

# Periodic celery tasks
CELERYBEAT_SCHEDULE = {
    'jira-work': {
        'task': 'services.tasks.process_jira_work',
        'schedule': crontab(minute='*/5'),
    },
}

# JIRA settings
JIRA_SERVER = 'http://54.154.50.144:8080/'
JIRA_USER = os.environ.get('JIRA_USER', '')
JIRA_PASSWORD = os.environ.get('JIRA_PASSWORD', '')
JIRA_PROJECT_KEY = 'SM'
JIRA_DUEIN_DAYS = 2

# Regex string that will only match valid phone numbers
# 12-123456
# ##-######
# Note: A few tests assume this regex; if you change it, re-run the
# tests and fix them.
PHONE_NUMBER_REGEX = r'^\d{2}-\d{6}$'

TEST_RUNNER = 'service_info.runner.CustomTestSuiteRunner'

# Use https when constructing links to ourselves?
# Generally True, we'll change to False in dev.py for running locally
SECURE_LINKS = True
