from django.db import models
from .aircraft_type import AircraftType
from .customer import Customer

class TailAircraftLookup(models.Model):
    tail_number = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tail_aircraft_lookup')
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.CASCADE, related_name='tail_aircraft_lookup')

    def __str__(self) -> str:
        return self.tail_number

    class Meta:
        ordering = ['tail_number']