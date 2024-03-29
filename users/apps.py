from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    verbose_name = "Tech support"

    def ready(self):
        try:
            import users.signals
        except ImportError:
            pass
