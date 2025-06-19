from django.db import models
from .customer import Customer
from .aircraft_type import AircraftType

class CustomerTail(models.Model):
    tail_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tails')
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.CASCADE, related_name='tails')
    is_active = models.BooleanField(default=True)
    has_flight_activity = models.BooleanField(default=True, help_text='Indicates if the tail has any flight activity associated with it for the last 10 days')