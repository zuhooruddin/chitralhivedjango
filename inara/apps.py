from django.apps import AppConfig


class InaraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inara'

    def ready(self):
        # Register signal handlers on app startup.
        from . import signals  # noqa: F401
