from django.apps import AppConfig


class RezerwacjaNipAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rezerwacja_nip_app'

    def ready(self):
        import rezerwacja_nip_app.signals
