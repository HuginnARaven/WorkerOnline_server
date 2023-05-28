from django.apps import AppConfig


class IotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'iot'

    def ready(self):
        try:
            import iot.signals
            from . import scheduler
            scheduler.start()

        except ImportError:
            print("iot app ImportError")
            pass
