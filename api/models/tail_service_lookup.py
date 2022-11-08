from django.db import models
from .service import Service
from .customer import Customer


class TailServiceLookup(models.Model):
    tail_number = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tail_service_lookup')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='tail_service_lookup')

    def __str__(self) -> str:
        return self.tail_number

    class Meta:
        ordering = ['tail_number']
