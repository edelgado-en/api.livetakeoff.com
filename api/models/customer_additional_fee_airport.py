from django.db import models
from .customer_additional_fee import CustomerAdditionalFee
from .airport import Airport

class CustomerAdditionalFeeAirport(models.Model):
    customer_additional_fee = models.ForeignKey(CustomerAdditionalFee, on_delete=models.CASCADE, related_name='airports')
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Customer Additional Fee Airports'