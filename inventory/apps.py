from django.apps import AppConfig
import os

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        # Only run if scheduler is enabled
        if os.environ.get('RUN_SCHEDULER', '').lower() == 'true':
            from .tasks import start_scheduler
            start_scheduler()
        

   