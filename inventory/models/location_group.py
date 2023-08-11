from django.db import models
from .group import Group
from .location import Location

class LocationGroup(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='location_groups')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='location_groups')

    def __str__(self) -> str:
        return f'{self.location.name} - {self.group.name}'
