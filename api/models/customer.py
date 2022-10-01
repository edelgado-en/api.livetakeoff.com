from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    billingAddress = models.TextField(blank=True, null=True)
    emailAddress = models.EmailField(blank=True, null=True, unique=True)
    #TODO: logo is an image. We can save this in the database
    billingInfo = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name