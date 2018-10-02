"""
.. _settings

Django settings for p_soc_auto project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/

:module:     p_soc_auto.settings

:contact:    ali.rahmat@phsa.ca
:contact:    serban.teodorescu@phsa.ca

:copyright:

    Copyright 2018 Provincial Health Service Authority
    of British Columbia

"""

import os
from kombu import Queue, Exchange


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5u7)@@#z0yr-$4q#enfc&20a6u6u-h1_nr^(z%fkqu3dx+y6ji'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*', ]


# Application definition

INSTALLED_APPS = [
    'rules_engine.apps.RulesEngineConfig',
    'orion_integration.apps.OrionIntegrationConfig',
    'p_soc_auto_base.apps.PSocAutoBaseConfig',
    'ssl_cert_tracker.apps.SslCertificatesConfig',
    'notifications.apps.NotificationsConfig',
    'dal',
    'dal_select2',
    'grappelli',
    'rangefilter',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django_celery_results',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'p_soc_auto.urls'

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

WSGI_APPLICATION = 'p_soc_auto.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'phsa_database',
        'HOST': '',
        'PASSWORD': 'phsa_db_password',
        'USER': 'phsa_db_user',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_ROOT = '/opt/phsa/p_soc_auto/static/'
STATIC_URL = '/static/'

MEDIA_ROOT = '/opt/phsa/p_soc_auto/media/'
MEDIA_URL = '/media/'

# orion logins
ORION_URL = 'https://orion.vch.ca:17778/SolarWinds/InformationService/v3/Json'
ORION_USER = 'CSTmonitor'
ORION_PASSWORD = 'phsa123'
ORION_VERIFY_SSL_CERT = False
ORION_TIMEOUT = (10.0, 22.0)
"""
:var ORION_TIMEOUT: the timeouts used by the `requests` module

    the values in the tuple are in seconds; the first value is the connection
    timeout, the second one is the read tiemout

"""

# celery settings
CELERY_BROKER_URL = 'amqp://guest:guest@localhost//'

CELERY_ACCEPT_CONTENT = ['json', 'pickle']
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_TASK_SERIALIZER = 'json'

CELERY_QUEUES = (
    Queue('rules', Exchange('rules'), routing_key='rules'),
    Queue('orion', Exchange('orion'), routing_key='orion'),
    Queue('nmap', Exchange('nmap'), routing_key='nmap'),
    Queue('ssl', Exchange('ssl'), routing_key='ssl'),
    Queue('shared', Exchange('shared'), routing_key='shared')
)

CELERY_DEFAULT_QUEUE = 'shared'
CELERY_DEFAULT_EXCHANGE = 'shared'
CELERY_DEFAULT_ROUTING_KEY = 'shared'


# service users
RULES_ENGINE_SERVICE_USER = 'phsa_rules_user'
NOTIFICATIONS_SERVICE_USER = 'phsa_notifications_user'

AJAX_LOOKUP_CHANNELS = {
    'fields': ('rules_engine.lookups', 'FieldNamesLookup')}

# common email settings
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp'
EMAIL_HOST = "smtp.healthbc.org"  # 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587
EMAIL_HOST_USER = 'ali.rahmat@phsa.ca'
EMAIL_HOST_PASSWORD = 'XXXXXXXX'


#=========================================================================
# # email settings for gmail
# # these will not work from 10.1.80.0
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'phsadev@gmail.com'
# EMAIL_HOST_PASSWORD = 'gaukscylgzzlavva'
#=========================================================================

#=========================================================================
# # temporary email settings with the smtp relay
# # these will only work from IP addresses that have been white-listed
EMAIL_HOST = "smtp.healthbc.org"  # 'smtp.gmail.com'
EMAIL_HOST_USER = 'serban.teodorescu@phsa.ca'
EMAIL_HOST_PASSWORD = ''
#=========================================================================
