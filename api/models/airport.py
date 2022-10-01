from django.db import models

class Airport(models.Model):
    initials = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['initials']