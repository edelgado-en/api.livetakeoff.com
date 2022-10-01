from unicodedata import name
from django.db import models

class Vendor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name