from django.db import models
from .location import Location

class LocationUser(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='location_user')
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='location_user')
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.user.username} - {self.location.name}'

        