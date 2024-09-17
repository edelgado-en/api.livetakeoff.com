from unicodedata import name
from django.db import models

class Vendor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    billing_address = models.CharField(max_length=255, blank=True, null=True)
    emails = models.CharField(max_length=255, blank=True, null=True, help_text='Comma separated list of emails')
    phone_numbers = models.CharField(max_length=255, blank=True, null=True, help_text='Comma separated list of phone numbers')
    logo = models.ImageField(upload_to='vendors/', blank=True)
    active = models.BooleanField(default=True)
    is_external = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
        