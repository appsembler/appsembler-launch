from .base import *
from datetime import timedelta

MEDIA_ROOT = os.path.join(get_env_variable('OPENSHIFT_DATA_DIR'), 'media')

STATIC_ROOT = os.path.join(get_env_variable('OPENSHIFT_REPO_DIR'), 'wsgi', 'static')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'appsemblerlaunch',  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': get_env_variable('OPENSHIFT_POSTGRESQL_DB_USERNAME'),
        'PASSWORD': get_env_variable('OPENSHIFT_POSTGRESQL_DB_PASSWORD'),
        'HOST': get_env_variable('OPENSHIFT_POSTGRESQL_DB_HOST'),                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': get_env_variable('OPENSHIFT_POSTGRESQL_DB_PORT'),                      # Set to empty string for default.
    }
}

INSTALLED_APPS += (
    'djrill',
    'raven.contrib.django.raven_compat',
)

# Sentry/Raven config
RAVEN_CONFIG = {
    'dsn': get_env_variable('SENTRY_DSN'),
}

# Email settings
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
MANDRILL_API_KEY = get_env_variable('MANDRILL_API_KEY')

# Celery settings
BROKER_URL = "redis://:{0}@{1}:{2}/0".format(get_env_variable('REDIS_PASSWORD'),
                                             get_env_variable('OPENSHIFT_REDIS_HOST'),
                                             get_env_variable('OPENSHIFT_REDIS_PORT'))

CELERYBEAT_SCHEDULE = {
    # 'app-expires-soon-notify': {
    #     'task': 'deployment.tasks.notify_expiring_apps',
    #     'schedule': timedelta(seconds=60),
    # },
    'destroy-expired-apps': {
        'task': 'deployment.tasks.destroy_expired_apps',
        'schedule': timedelta(seconds=60),
    },
}
