from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-production-secret-key'  # Change this!

DEBUG = False

ALLOWED_HOSTS = ['leonmarios.pythonanywhere.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email settings for production
EMAIL_HOST_USER = 'your-production-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-production-app-password'
DEFAULT_FROM_EMAIL = 'ΔΔCCSM <your-production-email@gmail.com>'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY' 