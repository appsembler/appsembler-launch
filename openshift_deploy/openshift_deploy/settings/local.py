from .base import *
from datetime import timedelta

DEBUG = True

# Email settings
EMAIL_HOST = 'mail.kset.org'
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True


INTERNAL_IPS = (
    '127.0.0.1',
)

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# Celery config
BROKER_URL = 'django://'

CELERYBEAT_SCHEDULE = {
    # 'app-expires-soon-notify': {
    #     'task': 'deployment.tasks.notify_expiring_apps',
    #     'schedule': timedelta(seconds=10),
    # },
    'destroy-expired-apps': {
        'task': 'deployment.tasks.destroy_expired_apps',
        'schedule': timedelta(seconds=10),
    },
}