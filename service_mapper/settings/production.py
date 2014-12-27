from service_mapper.settings.staging import *

# There should be only minor differences from staging

DATABASES['default']['NAME'] = 'service_mapper_production'
DATABASES['default']['USER'] = 'service_mapper_production'

EMAIL_SUBJECT_PREFIX = '[Service_Mapper Prod] '

# Uncomment if using celery worker configuration
BROKER_URL = 'amqp://service_mapper_production:%(BROKER_PASSWORD)s@%(BROKER_HOST)s/service_mapper_production' % os.environ
