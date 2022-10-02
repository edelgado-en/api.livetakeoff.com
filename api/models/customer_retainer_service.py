from tabnanny import verbose
from django.db import models
from .customer_settings import CustomerSettings
from .retainer_service import RetainerService

class CustomerRetainerService(models.Model):
    customer_setting = models.ForeignKey(CustomerSettings, on_delete=models.CASCADE, related_name='retainer_services')
    retainer_service = models.ForeignKey(RetainerService, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Customer Retainer Services'