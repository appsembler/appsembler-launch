from .base import *

MEDIA_ROOT = os.path.join(get_env_variable('OPENSHIFT_DATA_DIR'), 'media')

STATIC_ROOT = os.path.join(get_env_variable('OPENSHIFT_REPO_DIR'), 'wsgi', 'static')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(get_env_variable('OPENSHIFT_DATA_DIR'), 'sqlite3.db'),  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

INSTALLED_APPS += (
    'djrill',
)

# Email settings
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
MANDRILL_API_KEY = "qweGuAVYZPU4kWSZKg6fIw"

# Celery settings
BROKER_URL = 'redis://:ZTNiMGM0NDI5OGZjMWMxNDlhZmJmNG@127.5.78.2:16379/0'
