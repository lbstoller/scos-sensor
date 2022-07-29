"""Django settings for scos-sensor project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/

"""

import os
import sys
from os import path

from environs import Env

env = Env()

# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# Build paths inside the project like this: path.join(BASE_DIR, ...)
BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
REPO_ROOT = path.dirname(BASE_DIR)
# REPO_ROOT = env("APP_ROOT", default=None)
# if not REPO_ROOT:
#     REPO_ROOT = path.dirname(BASE_DIR)

FQDN = env("FQDN", "fqdn.unset")

DOCKER_TAG = env("DOCKER_TAG", default=None)
GIT_BRANCH = env("GIT_BRANCH", default=None)
if not DOCKER_TAG or DOCKER_TAG == "latest":
    VERSION_STRING = GIT_BRANCH
else:
    VERSION_STRING = DOCKER_TAG
    if VERSION_STRING.startswith("v"):
        VERSION_STRING = VERSION_STRING[1:]

STATIC_ROOT = path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

__cmd = path.split(sys.argv[0])[-1]
IN_DOCKER = env.bool("IN_DOCKER", default=False)
RUNNING_TESTS = "test" in __cmd
RUNNING_DEMO = env.bool("DEMO", default=False)
MOCK_SIGAN = env.bool("MOCK_SIGAN", default=False) or RUNNING_DEMO or RUNNING_TESTS
MOCK_SIGAN_RANDOM = env.bool("MOCK_SIGAN_RANDOM", default=False)


# Healthchecks - the existance of any of these indicates an unhealthy state
SDR_HEALTHCHECK_FILE = path.join(REPO_ROOT, "sdr_unhealthy")
SCHEDULER_HEALTHCHECK_FILE = path.join(REPO_ROOT, "scheduler_dead")

LICENSE_URL = "https://github.com/NTIA/scos-sensor/blob/master/LICENSE.md"

OPENAPI_FILE = path.join(REPO_ROOT, "docs", "openapi.json")

CONFIG_DIR = path.join(REPO_ROOT, "configs")
DRIVERS_DIR = path.join(REPO_ROOT, "drivers")

# JSON configs
# TODO remove calibration files, add instructions to set these in scos-usrp
if path.exists(path.join(CONFIG_DIR, "sensor_calibration.json")):
    SENSOR_CALIBRATION_FILE = path.join(CONFIG_DIR, "sensor_calibration.json")
if path.exists(path.join(CONFIG_DIR, "sigan_calibration.json")):
    SIGAN_CALIBRATION_FILE = path.join(CONFIG_DIR, "sigan_calibration.json")
if path.exists(path.join(CONFIG_DIR, "sensor_definition.json")):
    SENSOR_DEFINITION_FILE = path.join(CONFIG_DIR, "sensor_definition.json")
MEDIA_ROOT = path.join(REPO_ROOT, "files")
PRESELECTOR_CONFIG=path.join(CONFIG_DIR, "preselector_config.json")

# Cleanup any existing healtcheck files
try:
    os.remove(SDR_HEALTHCHECK_FILE)
except OSError:
    pass

# As defined in SigMF
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# https://docs.djangoproject.com/en/2.2/ref/settings/#internal-ips If
# IN_DOCKER, the IP address that needs to go here to enable the debugging
# toolbar can change each time the bridge network is brought down. It's
# possible to extract the correct address from an incoming request, so if
# IN_DOCKER and DEBUG=true, then the `api_v1_root` view will insert the correct
# IP when the first request comes in.
INTERNAL_IPS = ["127.0.0.1"]

# See /env.template
if not IN_DOCKER or RUNNING_TESTS:
    SECRET_KEY = "!j1&*$wnrkrtc-74cc7_^#n6r3om$6s#!fy=zkd_xp(gkikl+8"  # TODO not sure why this is set here
    DEBUG = True
    ALLOWED_HOSTS = []
else:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECRET_KEY = env.str("SECRET_KEY")
    DEBUG = env.bool("DEBUG", default=False)
    ALLOWED_HOSTS = env.str("DOMAINS").split() + env.str("IPS").split()
    POSTGRES_PASSWORD = env("POSTGRES_PASSWORD")

SESSION_COOKIE_SECURE = IN_DOCKER
CSRF_COOKIE_SECURE = IN_DOCKER

SESSION_COOKIE_AGE = 900  # seconds
SESSION_EXPIRE_SECONDS = 900  # seconds
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = "/api/auth/logout/?next=/api/v1/"

# Application definition

API_TITLE = "SCOS Sensor API"

API_DESCRIPTION = """A RESTful API for controlling a SCOS-compatible sensor.

# Errors

The API uses standard HTTP status codes to indicate the success or failure of
the API call. The body of the response will be JSON in the following format:

## 400 Bad Request (Parse Error)

```json
{
    "field_name": [
        "description of first error",
        "description of second error",
        ...
    ]
}
```

## 400 Bad Request (Protected Error)

```json
{
    "detail": "description of error",
    "protected_objects": [
        "url_to_protected_item_1",
        "url_to_protected_item_2",
        ...
    ]
}
```

## 409 Conflict (DB Integrity Error)

```json
{
    "detail": "description of error"
}
```

"""

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_yasg",  # OpenAPI generator
    # project-local apps
    "authentication.apps.AuthenticationConfig",
    "capabilities.apps.CapabilitiesConfig",
    "handlers.apps.HandlersConfig",
    "tasks.apps.TasksConfig",
    "schedule.apps.ScheduleConfig",
    "scheduler.apps.SchedulerConfig",
    "status.apps.StatusConfig",
    "sensor.apps.SensorConfig",  # global settings/utils, etc
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django_session_timeout.middleware.SessionTimeoutMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    INSTALLED_APPS.extend(
        [
            "debug_toolbar",
            "django_extensions",
        ]
    )

    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "sensor.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": ["sensor.templatetags.sensor_tags"],
        },
    }
]

WSGI_APPLICATION = "sensor.wsgi.application"

# Django Rest Framework
# http://www.django-rest-framework.org/

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "sensor.exceptions.exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "authentication.permissions.RequiredJWTRolePermissionOrIsSuperuser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",  # this should always point to latest stable api
    "ALLOWED_VERSIONS": ("v1",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DATETIME_FORMAT": DATETIME_FORMAT,
    "DATETIME_INPUT_FORMATS": ("iso-8601",),
    "COERCE_DECIMAL_TO_STRING": False,  # DecimalField should return floats
    "URL_FIELD_NAME": "self",  # RFC 42867
}

AUTHENTICATION = env("AUTHENTICATION", default="")
if AUTHENTICATION == "CERT":
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
        "authentication.auth.CertificateAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    )
else:
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    )


# https://drf-yasg.readthedocs.io/en/stable/settings.html
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {},
    "APIS_SORTER": "alpha",
    "OPERATIONS_SORTER": "method",
    "VALIDATOR_URL": None,
}

if AUTHENTICATION == "JWT":
    SWAGGER_SETTINGS["SECURITY_DEFINITIONS"]["oAuth2JWT"] = {
        "type": "oauth2",
        "description": (
            "OAuth2 authentication using resource owner password flow."
            "This is done by verifing JWT bearer tokens signed with RS256 algorithm."
            "The JWT_PUBLIC_KEY_FILE setting controls the public key used for signature verification."
            "Only authorizes users who have an authority matching the REQUIRED_ROLE setting."
            "For more information, see https://tools.ietf.org/html/rfc6749#section-4.3."
        ),
        "flows": {"password": {"scopes": {}}},  # scopes are not used
    }
else:
    SWAGGER_SETTINGS["SECURITY_DEFINITIONS"]["token"] = {
        "type": "apiKey",
        "description": (
            "Tokens are automatically generated for all users. You can "
            "view yours by going to your User Details view in the "
            "browsable API at `/api/v1/users/me` and looking for the "
            "`auth_token` key. New user accounts do not initially "
            "have a password and so can not log in to the browsable API. "
            "To set a password for a user (for testing purposes), an "
            "admin can do that in the Sensor Configuration Portal, but "
            "only the account's token should be stored and used for "
            "general purpose API access. "
            'Example cURL call: `curl -kLsS -H "Authorization: Token'
            ' 529c30e6e04b3b546f2e073e879b75fdfa147c15" '
            "https://localhost/api/v1`"
        ),
        "name": "Token",
        "in": "header",
    }

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

if RUNNING_TESTS or RUNNING_DEMO:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            # "NAME": ":memory:"
            "NAME": "test.db",  # temporary workaround for https://github.com/pytest-dev/pytest-django/issues/783
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": "db",
            "PORT": "5432",
        }
    }

if not IN_DOCKER:
    DATABASES["default"]["HOST"] = "localhost"

# Delete oldest TaskResult (and related acquisitions) of current ScheduleEntry if MAX_DISK_USAGE exceeded
MAX_DISK_USAGE = env.int("MAX_DISK_USAGE", default=85)  # percent
# Display at most MAX_TASK_QUEUE upcoming tasks in /tasks/upcoming
MAX_TASK_QUEUE = 50

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "authentication.User"

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOGLEVEL = "DEBUG" if DEBUG else "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "[%(asctime)s] [%(levelname)s] %(message)s"}},
    "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "loggers": {
        "actions": {"handlers": ["console"], "level": LOGLEVEL},
        "authentication": {"handlers": ["console"], "level": LOGLEVEL},
        "capabilities": {"handlers": ["console"], "level": LOGLEVEL},
        "handlers": {"handlers": ["console"], "level": LOGLEVEL},
        "schedule": {"handlers": ["console"], "level": LOGLEVEL},
        "scheduler": {"handlers": ["console"], "level": LOGLEVEL},
        "sensor": {"handlers": ["console"], "level": LOGLEVEL},
        "status": {"handlers": ["console"], "level": LOGLEVEL},
        "tasks": {"handlers": ["console"], "level": LOGLEVEL},
        "scos_actions": {"handlers": ["console"], "level": LOGLEVEL},
        "scos_usrp": {"handlers": ["console"], "level": LOGLEVEL},
        "scos_sensor_keysight": {"handlers": ["console"], "level": LOGLEVEL},
    },
}


CALLBACK_SSL_VERIFICATION = env.bool("CALLBACK_SSL_VERIFICATION", default=True)
# OAuth Password Flow Authentication
CALLBACK_AUTHENTICATION = env("CALLBACK_AUTHENTICATION", default="")
CLIENT_ID = env("CLIENT_ID", default="")
CLIENT_SECRET = env("CLIENT_SECRET", default="")
USER_NAME = CLIENT_ID
PASSWORD = CLIENT_SECRET

OAUTH_TOKEN_URL = env("OAUTH_TOKEN_URL", default="")
CERTS_DIR = path.join(CONFIG_DIR, "certs")
# Sensor certificate with private key used as client cert
PATH_TO_CLIENT_CERT = env("PATH_TO_CLIENT_CERT", default="")
if PATH_TO_CLIENT_CERT != "":
    PATH_TO_CLIENT_CERT = path.join(CERTS_DIR, PATH_TO_CLIENT_CERT)
# Trusted Certificate Authority certificate to verify authserver and callback URL server certificate
PATH_TO_VERIFY_CERT = env("PATH_TO_VERIFY_CERT", default="")
if PATH_TO_VERIFY_CERT != "":
    PATH_TO_VERIFY_CERT = path.join(CERTS_DIR, PATH_TO_VERIFY_CERT)
# Public key to verify JWT token
PATH_TO_JWT_PUBLIC_KEY = env.str("PATH_TO_JWT_PUBLIC_KEY", default="")
if PATH_TO_JWT_PUBLIC_KEY != "":
    PATH_TO_JWT_PUBLIC_KEY = path.join(CERTS_DIR, PATH_TO_JWT_PUBLIC_KEY)
# Required role from JWT token to access API
REQUIRED_ROLE = "ROLE_MANAGER"

PRESELECTOR_CONFIG = env.str('PRESELECTOR_CONFIG', default=path.join(CONFIG_DIR, 'preselector_config.json'))
PRESELECTOR_MODULE = env.str('PRESELECTOR_MODULE', default='its_preselector.web_relay_preselector')
PRESELECTOR_CLASS = env.str('PRESELECTOR_CLASS', default='WebRelayPreselector')
