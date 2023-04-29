from django.apps import AppConfig


class CompaniesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'companies'

    def ready(self):
        try:
            import companies.signals
        except ImportError:
            pass
