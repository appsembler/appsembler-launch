from .base import *
from datetime import timedelta

DEBUG = True

# Email settings
EMAIL_HOST = 'mail.kset.org'
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'appsemblerlaunch',  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}


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
        'schedule': timedelta(seconds=1000),
    },
}