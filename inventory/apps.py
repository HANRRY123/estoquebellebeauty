from django.apps import AppConfig
from django.db import ProgrammingError, OperationalError


class InventoryConfig(AppConfig):
    name = 'inventory'

    def ready(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        except (ProgrammingError, OperationalError):
            pass
