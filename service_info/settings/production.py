from service_info.settings.staging import *  # noqa

# There should be only minor differences from staging

DATABASES['default']['NAME'] = 'service_info_production'
DATABASES['default']['USER'] = 'service_info_production'

EMAIL_SUBJECT_PREFIX = '[ServiceInfo Prod] '
DEFAULT_FROM_EMAIL = 'noreply@rescue.org'

SITE_ID = PRODUCTION_SITE_ID

# Uncomment if using celery worker configuration
if 'BROKER_PASSWORD' in os.environ:
    BROKER_URL = 'amqp://service_info_production:%(BROKER_PASSWORD)s@%(BROKER_HOST)s' \
                 '/service_info_production' % os.environ

# Production JIRA projects:
JIRA_SERVICES_PROJECT_KEY = 'SM'
JIRA_FEEDBACK_PROJECT_KEY = 'LBF'
