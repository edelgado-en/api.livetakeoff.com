from django.db import models
from .airport import Airport


class UserAvailableAirport(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='available_airports')
    airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='available_users')
