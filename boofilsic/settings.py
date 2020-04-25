"""
Django settings for boofilsic project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import psycopg2.extensions

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '65n29puv(7ay3pft#*zj9r%8dhv%n*$nizf2#4u(8eartit%da'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'rest_framework',
    'books.apps.BooksConfig',
    'common.apps.CommonConfig',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'boofilsic.urls'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.ResultsSetPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.authentication.SimpleAuthentication',
    ],
    'UNAUTHENTICATED_USER': None,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

TEMPLATES = [
    # {
    #     'BACKEND': 'django.template.backends.django.DjangoTemplates',
    #     'DIRS': [],
    #     'APP_DIRS': True,
    #     'OPTIONS': {
    #         'context_processors': [
    #             'django.template.context_processors.debug',
    #             'django.template.context_processors.request',
    #             # 'django.contrib.auth.context_processors.auth',
    #             # 'django.contrib.messages.context_processors.messages',
    #         ],
    #     },
    # },
]

WSGI_APPLICATION = 'boofilsic.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# see https://stackoverflow.com/questions/32773049/how-to-remove-index-varchar-pattern-ops-in-a-django-1-8-migration
# to optimize database schema
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'donotban',
        'USER': 'donotban',
        'PASSWORD': 'pleasedonotban',
        'HOST': '49.233.200.133',
        'OPTIONS': {
            'client_encoding': 'UTF8',
            # 'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_DEFAULT,
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

