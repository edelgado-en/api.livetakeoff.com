from django.db import models
from .customer_discount import CustomerDiscount
from .service import Service

class CustomerDiscountService(models.Model):
    customer_discount = models.ForeignKey(CustomerDiscount, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Customer Discount Service'