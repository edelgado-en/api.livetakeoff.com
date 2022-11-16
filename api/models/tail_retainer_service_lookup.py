from django.db import models
from .retainer_service import RetainerService
from .customer import Customer


class TailRetainerServiceLookup(models.Model):
    tail_number = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tail_retainer_service_lookup')
    retainer_service = models.ForeignKey(RetainerService, on_delete=models.CASCADE, related_name='tail_retainer_service_lookup')

    def __str__(self) -> str:
        return self.tail_number

    class Meta:
        ordering = ['tail_number']
