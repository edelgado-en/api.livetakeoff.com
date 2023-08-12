from django.db import models
from .location import Location
from .item import Item
from .brand import Brand

class LocationItem(models.Model):

    status_choices = (
        ('C', 'Confirmed'),
        ('U', 'Unconfirmed'),
    )

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='location_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='location_items')
    quantity = models.IntegerField(default=0)
    minimum_required = models.IntegerField(default=0, null=True, blank=True)
    threshold = models.IntegerField(default=0, null=True, blank=True)
    status = models.CharField(max_length=1, choices=status_choices, default='U',
                             help_text='User will have the option to change to confirmed while in the Checking Inventory View. \
                                       When an Item gets adjusted by either adding or subtracting, the status will change to unconfirmed.')

    def __str__(self) -> str:
        return f'{self.item.name} - {self.location.name}'