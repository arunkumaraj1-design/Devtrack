import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-secret-key'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'issues',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'devtrack.urls'

TEMPLATES = []

WSGI_APPLICATION = 'devtrack.wsgi.application'

# Minimal DB settings not used

STATIC_URL = '/static/'
