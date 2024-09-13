from django.db import models
from .job import Job

class InvoicedDiscount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('S', 'By Service'),
        ('A', 'By Airport'),
        ('G', 'General'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='invoiced_discounts')
    discount = models.IntegerField()
    discount_dollar_amount = models.DecimalField(max_digits=9, decimal_places=2)
    type = models.CharField(max_length=1, choices=DISCOUNT_TYPE_CHOICES)
    percentage = models.BooleanField(default=False)