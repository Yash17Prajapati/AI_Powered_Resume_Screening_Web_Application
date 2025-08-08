from pathlib import Path
from mongoengine import connect
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
global_email=None
# print(BASE_DIR)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^dd^(lpuf#8y38r&2%jycq)n@d(@w1t1&9!(19n5l1z_mhw6zv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user',
    'recruiter',
    'rest_framework'
]
# Email Settings
# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465  # Use 465 for SSL
EMAIL_USE_TLS = False  # TLS should be False when using SSL
EMAIL_USE_SSL = True  # SSL should be True when using port 465
EMAIL_HOST_USER = 'udiman03@gmail.com'
EMAIL_HOST_PASSWORD = 'xalxxjesqoowwbww'  # Your Google App Password (no spaces)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # Ensures consistency in outgoing emails
      # Your email password
X_FRAME_OPTIONS = 'ALLOWALL'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]
# MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
ROOT_URLCONF = 'job_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.getcwd(),'job_portal','templates'),os.path.join(os.getcwd(),'recruiter','templates'),os.path.join(os.getcwd(),'user','templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'job_portal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

RECRUITER_DB_ALIAS = 'recruiter_db'
connect(
    db='recruiter_db',  # Replace with your recruiter database name
    alias=RECRUITER_DB_ALIAS,
    host='mongodb://localhost:27017/recruiter_db',  # Update the URI if necessary
)
USER_DB_ALIAS = 'user_db'
connect(
    db='user',  # Replace with your user database name
    alias=USER_DB_ALIAS,
    host='mongodb://localhost:27017/user',  # Update the URI if necessary
)

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR/'job_portal' /'staticfiles'

# List additional directories to search for static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'job_portal','static'),
    os.path.join(BASE_DIR,'recruiter','static'),
    os.path.join(BASE_DIR,'user','static')
]
# print(STATICFILES_DIRS)
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
