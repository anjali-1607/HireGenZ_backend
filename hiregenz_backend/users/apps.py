from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration class for the 'users' app.
    Ensures that signals are imported and registered when the app is ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        """
        Override the ready method to import the signals module.
        This ensures the signals are connected when the app initializes.
        """
        import users.signals   # noqa
