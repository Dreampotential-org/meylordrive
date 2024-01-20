import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6xcxxio+$*i^*u*-tj$#zgajf!sjv#rf7l6s4jm^l@s#zv%)!3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*', 'beachcomber.usepam.com', 'localhost', '127.0.0.1']

BASE_URL = 'app.usepam.com'
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'AKIARWLPGYIKWTF4OEPZ'
AWS_SECRET_ACCESS_KEY = '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'
DEFAULT_FROM_EMAIL = 'noreply@useiam.com'
AWS_SES_REGION_NAME = 'us-east-2'
AWS_SES_REGION_ENDPOINT = 'email.us-east-2.amazonaws.com'
SITE_ID = 1

SLACK_API_KEY = "xoxb-790630255906-1844871421842-FFFWwP6KQT2eIsjTBHA8fsUR"
SLACK_CHANNEL = "#debug"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'xppda.apps.DappxConfig',
    'api',
    'magic_link',
    'drf_yasg',
    'dbbackup',
]

# CORS_ORIGIN_WHITELIST = ['v2-local.postmunk.me']
CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'dprojx.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR, ],
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

WSGI_APPLICATION = 'dprojx.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
db_user = os.environ.get('db_user', 'postgresuser')
db_password = os.environ.get('db_password', 'postgrespassword')
db_name = os.environ.get('db_user', 'postgres')
db_host = os.environ.get('db_host', 'localhost')
db_port = os.environ.get('db_port', '5443')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_name,
        'USER': db_user,
        'HOST': db_host,
        'PORT': db_port,
        'PASSWORD': db_password,

    }
}

website_url = 'https://localhost:80000/?token='

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [STATIC_DIR, ]
STATIC_ROOT = '/home/web/codes/static/'
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'
LOGIN_URL = '/xppda/user_login/'
CSRF_COOKIE_HTTPONLY = False

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

WEBSITE_URL = 'https://m.useiam.com/'
SERVER_URL = 'https://prod-api.useiam.com/'


# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_STORAGE_BUCKET_NAME = 'useiamstorage'
# AWS_S3_REGION_NAME = 'us-west-2'
# AWS_ACCESS_KEY_ID = 'AKIAU7EQAGZOEBB6KESL'
# AWS_SECRET_ACCESS_KEY = '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'

try:
    from settings_local import *
except ImportError:
    pass


MAGIC_LINK = {
    "DEFAULT_EXPIRY": 300,
    "DEFAULT_REDIRECT": "/",
    "AUTHENTICATION_BACKEND": "django.contrib.auth.backends.ModelBackend",
    "SESSION_EXPIRY": 7 * 24 * 60 * 60
}
