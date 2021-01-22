"""
Django settings for wyspp project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k9!3grj-67posaa!jthqs)_f365ti5ku)@aa3+99ivuq9^*d(g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    # Packages
    'fcm_django',
    'rest_framework',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',

    # Apps
    'REST'
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'REST.authentication.CustomSocialAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

JWT_AUTH = {
    # 'JWT_VERIFY': True,
    # 'JWT_VERIFY_EXPIRATION': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=3000),
    # 'JWT_AUTH_HEADER_PREFIX': 'JWT',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
    ]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'auth'
]


ROOT_URLCONF = 'wyspp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'wyspp.wsgi.application'

APPEND_SLASH = False
# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'wyspp_test',
        'USER': 'test_db_admin',
        'PASSWORD': 'm33x2Hgig4auKte',
        'HOST': '35.238.55.198',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ='../proud-reality-297821-98c3dd971666.json'

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'


FIREBASE_API_KEY = "AAAA3B8fkv0:APA91bHUVpSx01tN6-B9c1QkD86Af_6FotW1LpBJtrcvpmVKWgUk1zvyDHLPKnT8f6iYdBBL-ms1Gd5GWD3oihZFJq8lhMPW7eb7SbyVlPsGSNKHYlshHIzv4bFPuVKIqZ-cLPjUwnjp"

AUTHENTICATION_BACKENDS = (

    # Facebook OAuth2
    'social_core.backends.facebook.FacebookAppOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',

    # django-rest-framework-social-oauth2
    'rest_framework_social_oauth2.backends.DjangoOAuth2',

    # Django
    'django.contrib.auth.backends.ModelBackend',

    'social_core.backends.google.GoogleOAuth2',

    'social.backends.twitter.TwitterOAuth'
)
# https://developers.google.com/oauthplayground

SOCIAL_AUTH_FACEBOOK_KEY = '318521415986909'
SOCIAL_AUTH_FACEBOOK_SECRET = '9db25139db4a6f1cb9e3d75c574d02c7'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '788430071697-29t3dc2lt7suuf9446c3jp1ilkge469o.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'bHqtXy8xxVON7-x524U_ZFai'
FACEBOOK_EXTENDED_PERMISSIONS = ['username']
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_TWITTER_KEY = 'sMZgBv3hDLANehy8mSNqFUVGm'
SOCIAL_AUTH_TWITTER_SECRET = 'yYTpZW1jKXwngs0x9XKa5WFkbZF54IJgiaysrEkT5jbjDIRdXy'
# Define SOCIAL_AUTH_FACEBOOK_SCOPE to get extra permissions from Facebook.
# Email is not sent by default, to get it, you must request the email permission.
SOCIAL_AUTH_FACEBOOK_SCOPE = ['username']
# SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
#     'fields': 'id, name, username'
# }
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email','first_name','last_name']
