from django.db import models
from .location import Location
from .location_item import LocationItem

class LocationItemActivity(models.Model):

    activity_type_choices = (
        ('A', 'Add'),
        ('M', 'Move'),
        ('S', 'Subtract'),
        ('C', 'Confirm'),
    )

    location_item = models.ForeignKey(LocationItem, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=1, choices=activity_type_choices)
    quantity = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Summation of cost per unit and quantity')
    moved_from = models.ForeignKey(Location, on_delete=models.PROTECT, blank=True, null=True, related_name='moved_from')
    moved_to = models.ForeignKey(Location, on_delete=models.PROTECT, blank=True, null=True, related_name='moved_to')
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f'{self.item.name} - {self.location.name} - {self.activity_type} - {self.quantity} - {self.activity_date}'