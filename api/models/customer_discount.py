from django.db import models
from .customer_settings import CustomerSettings

class CustomerDiscount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('S', 'By Service'),
        ('A', 'By Airport'),
        ('G', 'General'),
    ]

    customer_setting = models.ForeignKey(CustomerSettings, on_delete=models.CASCADE, related_name='discounts')
    discount = models.IntegerField()
    type = models.CharField(max_length=1, choices=DISCOUNT_TYPE_CHOICES)

    def __str__(self) -> str:
        return 'id: ' + str(self.id) + ' discount: ' + str(self.discount) + '%'

    class Meta:
        verbose_name_plural = 'Customer Discounts'