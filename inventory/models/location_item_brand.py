from django.db import models
from .brand import Brand
from .location_item import LocationItem

class LocationItemBrand(models.Model):
    location_item = models.ForeignKey(LocationItem, on_delete=models.CASCADE, related_name='location_item_brands')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='location_item_brands')

    def __str__(self) -> str:
        return f'{self.location_item.item.name} - {self.brand.name}'
    
