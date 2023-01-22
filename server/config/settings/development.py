from .base import *
from .base import env

DEBUG = env("DJANGO_DEBUG", default="true") == "true"

SECRET_KEY = env("DJANGO_SECRET_KEY")

CORS_ORIGIN_ALLOW_ALL = True

#########
# email #
#########

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

########################
# static & media files #
########################

STATICFILES_STORAGE = "safers.core.storage.LocalStaticStorage"
DEFAULT_FILE_STORAGE = "safers.core.storage.LocalMediaStorage"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "_static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "_media"

# These next env vars aren't used in development, but they still ought
# to be defined so that the classes in "storages.py" module can load...

STATIC_LOCATION = ""
STATIC_DEFAULT_ACL = ""
PUBLIC_MEDIA_LOCATION = ""
PUBLIC_MEDIA_DEFAULT_ACL = ""
PRIVATE_MEDIA_LOCATION = ""
PRIVATE_MEDIA_DEFAULT_ACL = ""

###########
# logging #
###########

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s]: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

###########
# backups #
###########

DBBACKUP_STORAGE = "safers.core.storage.LocalMediaStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": f"{MEDIA_ROOT}/backups/"}

#############
# profiling #
#############

# see "https://gist.github.com/douglasmiranda/9de51aaba14543851ca3"
# for tips about making django_debug_toolbar to play nicely w/ Docker

import socket

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "config.middleware.JSONDebugToolbarMiddleware",
    # "silk.middleware.SilkyMiddleware",
    # "django_cprofile_middleware.middleware.ProfilerMiddleware",
]

DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = False

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TEMPLATE_CONTEXT": True,
    "SHOW_COLLAPSED": True,
    # "SHOW_TOOLBAR_CALLBACK": "safers.utils.show_toolbar",
}
DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
    # TODO: THIS WILL NOT WORK B/C OF https://github.com/pympler/pympler/pull/99
    # TODO: IN THE MEANTIME I'VE WRITTEN MY OWN DECORATOR THAT ACCOMPLISHES THE SAME THING
    # 'pympler.panels.MemoryPanel',
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
]

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]
