from django.db import models
from .price_list import PriceList
from .aircraft_type import AircraftType
from .service import Service

class PriceListEntries(models.Model):
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name='entries')
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Price List Entries'