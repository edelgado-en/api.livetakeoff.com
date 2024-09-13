from django.db import models
from .job import Job

class InvoicedService(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='invoiced_services')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=9, decimal_places=2)