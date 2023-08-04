from django.db import models
from .item import Item
from .tag import Tag

class ItemTag(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT, related_name='item_tags')

    def __str__(self):
        return str(self.item.id) + ' - ' + self.tag.name
    
