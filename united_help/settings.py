from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import firebase_admin
from firebase_admin import credentials
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-87mkw^d0!3#ccczhk0p0b@hr&eq)i=&d5##re%#1fbw%89&y6n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

cred = credentials.Certificate('ua-org-united-help-firebase-adminsdk.json')
firebase_admin.initialize_app(cred)


ALLOWED_HOSTS = ['united-help.pp.ua/', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://united-help.pp.ua/', 'http://localhost', 'http://127.0.0.1',
                        'http://localhost:8000', 'http://127.0.0.1:8000']

sentry_sdk.init(
    dsn="https://33078d724f4d4c04aff31f10b8f71725@sentry.fyuzd.live/6",
    integrations=[DjangoIntegration()],

    traces_sample_rate=1.0,

    send_default_pii=True,
    _experiments={
        "profiles_sample_rate": 1.0,
      },
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'phonenumber_field',
    'oauth2_provider',
    'social_django',
    'drf_social_oauth2',
    'united_help.apps.UnitedHelpConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'debug_toolbar',
    'rest_framework_simplejwt',
    'django_filters',
]

REST_FRAMEWORK = {
    # YOUR SETTINGS
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'drf_social_oauth2.authentication.SocialAuthentication',
    ),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Project API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
ROOT_URLCONF = 'united_help.urls'


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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'united_help.wsgi.application'

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
    }
}
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Kyiv'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'media/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'
BASE_URL = ''

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


FACEBOOK_SECRET_KEY = 'be6859ee267101c262db779cd948c2a1'
