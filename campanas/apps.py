from django.apps import AppConfig


class CampanasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'campanas'

    def ready(self):
        import campanas.hooks
    
    def ready(self):
        import campanas.signals