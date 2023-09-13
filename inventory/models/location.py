from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    enable_notifications = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name