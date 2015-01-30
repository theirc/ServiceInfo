from service_info.settings.staging import *  # noqa

DATABASES['default']['NAME'] = 'service_info_vagrant'
DATABASES['default']['USER'] = 'service_info_vagrant'

# Uncomment if using celery worker configuration
if 'BROKER_PASSWORD' in os.environ:
    BROKER_URL = 'amqp://service_info_vagrant:%(BROKER_PASSWORD)s@%(BROKER_HOST)s' \
                 '/service_info_vagrant' % os.environ


# Override settings here
