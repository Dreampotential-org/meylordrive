"""
Django settings for web project.

Generated by 'django-admin startproject' using Django 2.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

from rest_framework.settings import api_settings
from datetime import timedelta
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR='/data'
#MEDIA_URL='/data'
MEDIA_ROOT='/data'
CSRF_TRUSTED_ORIGINS = ['http://localhost',
                        'http://127.0.0.1',
                        'https://1.dreampotential.org',
                        'https://api.dreampotential.org',
                        'https://api.alt-r.world']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z@g8x(zh990d)ti@6)^a7ng2=t21_)dkwfs4n50d#(v@dy@f=r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
CSRF_COOKIE_SECURE = False

ALLOWED_HOSTS = ['*']

CSRF_COOKIE_HTTPONLY = False

# Application definition

INSTALLED_APPS = [
    'youtube_downloader',
    'xppda',
    'dprojx',
    'channels',
    'daphne',
    'mailapi',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'drf_yasg',
    'tasks',
    'agent',
    'rest_framework',
    'django_rest_passwordreset',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'knox',
    'corsheaders',
    'usersystem',
    'spotify',
    'project',
    'api',
    'server_websocket',
    'storage',
    'social_django',
    'ai',
    'livestats',
    'drive',
    'checkout',
    'clickads',
    'ashe',
    'awipu',



]
from pathlib import Path

SITE_ID = 1  # Change this to the ID of the site you want to use
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Use os.path.join to construct the path
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'
# STATIC_URL = '/static/'
# STATICFILES_DIRS = [BASE_DIR / 'static']
# STATIC_ROOT = BASE_DIR / 'staticfiles'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #    'django.middleware.csrf.CsrfViewMiddleware',
    # 'channels',
    # 'channels.auth.AuthenticationMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
   'social_django.middleware.SocialAuthExceptionMiddleware', 


]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = False
CORS_ORIGIN_ALLOW_ALL = True


STRIPE_PRICE_ID = 'price_1JfvdUGq4mM9DwWGFIIE1j99'
STRIPE_PUBLISHABLE_KEY = 'pk_test_x97eNoQQtQDTurBY7lrq1yME005Ntt2hOK'
STRIPE_SECRET_KEY = 'sk_test_51GPZU2Gq4mM9DwWGVtsyD1imIC3xNNEfNqYzGuWryfWT8ok25STRDnb4XORmCOv2sqDOYhKRbdowt1SAhjmGyFYT00kNM75J9r'
#
# STRIPE_PRICE_ID = 'price_1Nv8EOGq4mM9DwWGFZTFIhlX'
# STRIPE_PUBLISHABLE_KEY = 'pk_live_6nE4LbMc80WJmAD3PoVohLvM00KdBRzc1N'
# STRIPE_SECRET_KEY = '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'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',

            ],
        },
    },
]

# WSGI_APPLICATION = 'web.wsgi.application'
# ASGI_APPLICATION = "server_websocket.routing.application"
# settings.py
ASGI_APPLICATION = 'server_websocket.routing.application'


ROOT_URLCONF = 'web.urls'

# ASGI_APPLICATION = 'web.routing.application'
ASGI_APPLICATION = "web.asgi.application"



# CHANNELS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             # other configurations...
#             "hosts": [('agentstat.com', 6379)],
#         },
#         'ROUTING': 'web.routing.application',  # adjust based on your project structure
#     },
# }
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

dbpassword = os.environ.get('dbpassword', 'postgres')
dbuser = os.environ.get('dbuser', 'postgres')
dbhost = os.environ.get('dbhost', 'dreampotential.org')
dbport = os.environ.get('dbport', '5775')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': dbuser,
        'HOST': dbhost,
        'PORT': dbport,
        'PASSWORD': dbpassword,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Make knox’s Token Authentication default
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('knox.auth.TokenAuthentication',),
}

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('agentstat.com', 6379)],
#         },
#     },
# }

# KNOX
REST_KNOX = {
    'USER_SERIALIZER': 'usersystem.serializer.UserSerializer',
}

REST_KNOX = {
    'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(hours=10),
    'USER_SERIALIZER': 'knox.serializers.UserSerializer',
    'TOKEN_LIMIT_PER_USER': None,
    'AUTO_REFRESH': False,
    #   'EXPIRY_DATETIME_FORMAT': api_settings.DATETME_FORMAT,
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = 'AKIARWLPGYIKRQXN5VXR'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'sfappv2'

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

ALLOWED_HOSTS = ['*', "api.dreampotential.org"]

# # Email
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.email.us-chicago-1.oci.oraclecloud.com'
# EMAIL_HOST_USER = 'ocid1.user.oc1..aaaaaaaae4z6ngwxbkxg6qn6z3ogpsyt4pryvcqp4aq76tgr5b6zijkglrnq@ocid1.tenancy.oc1..aaaaaaaasq5eo5hshbwevjpvqk52wwb35l4vh4lwwp3rzuxq5f2x4m3pji6a.2j.com'
# EMAIL_HOST_PASSWORD = '&.)S_hq6r)RSZZ<hHXI-'
# EMAIL_PORT = 587


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER='shaiknadeem@gmai.com'
EMAIL_HOST_PASSWORD='vzviuawilbewzjir'
EMAIL_USE_TLS= True
EMAIL_USE_SSL=False





STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

APPEND_SLASH = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_KNOX = {
    'TOKEN_TTL': None,  # will create tokens that never expire
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '1080935805006-grv71s87oklr4eoos6h8m0no6rjtnrt7.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY ='1080935805006-grv71s87oklr4eoos6h8m0no6rjtnrt7.apps.googleusercontent.com'
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='GOCSPX-Vn_olHbd6biA408Ky2UU5¡LHoU3x'
SOCIAL_AUTH_REDIRECT_URI = 'https://api.dreampotential.org/social-auth/complete/google-oauth2/'
USE_X_FORWARDED_HOST = True
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
