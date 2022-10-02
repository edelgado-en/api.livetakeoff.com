from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    billingAddress = models.TextField(blank=True, null=True)
    emailAddress = models.EmailField(blank=True, null=True, unique=True)
    logo = models.ImageField(upload_to='images/', blank=True)
    billingInfo = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name