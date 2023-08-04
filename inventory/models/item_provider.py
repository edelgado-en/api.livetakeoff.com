from django.db import models
from .item import Item
from .provider import Provider

class ItemProvider(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='providers')
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT, related_name='item_providers')

    def __str__(self):
        return str(self.item.id) + ' - ' + self.provider.name
    
