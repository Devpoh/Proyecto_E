from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        """
        ✅ Registrar signals cuando la app está lista
        
        Los signals se importan aquí para evitar circular imports
        y asegurar que se registren correctamente.
        """
        import api.signals  # noqa: F401
