from email.policy import default
from tabnanny import verbose
from django.db import models
from .customer import Customer
from .service import Service

class CustomerService(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Customer Services'