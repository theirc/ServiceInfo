import sys

from service_info.settings.base import *  # noqa

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'debug_toolbar',
)

INTERNAL_IPS = ('127.0.0.1', )

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SOUTH_TESTS_MIGRATE = True

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

SITE_ID = DEV_SITE_ID

CMS_LANGUAGES[SITE_ID] = CMS_LANGUAGES_FOR_SITE

# Use https when constructing links to ourselves?
# Generally True, we'll change to False in dev.py for running locally
SECURE_LINKS = False

# Special test settings
if 'test' in sys.argv:
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.SHA1PasswordHasher',
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

    # Dummy JIRA projects (we need some settings or JIRA code short-circuits
    # and we can't test it)
    JIRA_SERVICES_PROJECT_KEY = 'DUMMYSM'
    JIRA_FEEDBACK_PROJECT_KEY = 'DUMMYLBF'
