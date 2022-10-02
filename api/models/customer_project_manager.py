from tabnanny import verbose
from django.db import models
from .customer_settings import CustomerSettings

class CustomerProjectManager(models.Model):
    customer_setting = models.ForeignKey(CustomerSettings, on_delete=models.CASCADE, related_name='project_managers')
    project_manager = models.ForeignKey('auth.User', on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = 'Customer Project Managers'