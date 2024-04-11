from django.db import models
from .customer_additional_fee import CustomerAdditionalFee
from .airport import Airport

class CustomerAdditionalFeeVendor(models.Model):
    customer_additional_fee = models.ForeignKey(CustomerAdditionalFee, on_delete=models.CASCADE, related_name='vendors')
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Customer Additional Fee Vendors'