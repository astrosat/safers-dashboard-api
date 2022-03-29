from threading import Thread

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RMQConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'safers.rmq'
    verbose_name = _("Safers RMQ")

    def ready(self):

        try:
            # register any checks...
            import safers.rmq.checks
        except ImportError:
            pass

        try:
            # register any signals...
            import safers.rmq.signals
        except ImportError:
            pass

        thread = Thread(name="rmq_thread", daemon=True, target=self.start_rmq)
        thread.start()

    def start_rmq(self):

        from safers.rmq import RMQ
        rmq = RMQ()
        rmq.subscribe()
