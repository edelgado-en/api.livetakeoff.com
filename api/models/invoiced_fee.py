from django.db import models
from .job import Job

class InvoicedFee(models.Model):
    FEE_TYPE_CHOICES = [
        ('F', 'FBO Fee'),
        ('A', 'Travel Fees'),
        ('G', 'General'),
        ('V', 'Higher Vendor Price'),
        ('M', 'Management Fees')
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='invoiced_fees')
    fee = models.DecimalField(max_digits=9, decimal_places=2)
    fee_dollar_amount = models.DecimalField(max_digits=9, decimal_places=2)
    type = models.CharField(max_length=1, choices=FEE_TYPE_CHOICES)
    percentage = models.BooleanField(default=False)