from django.db import models
from .customer_discount import CustomerDiscount
from .airport import Airport

class CustomerDiscountAirport(models.Model):
    customer_discount = models.ForeignKey(CustomerDiscount, on_delete=models.CASCADE, related_name='airports')
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Customer Discount Airport'