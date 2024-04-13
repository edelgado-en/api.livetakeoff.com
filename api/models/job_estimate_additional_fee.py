from django.db import models
from .job_estimate import JobEstimate


class JobEstimateAdditionalFee(models.Model):
    FEE_TYPE_CHOICES = [
        ('F', 'FBO Fee'),
        ('A', 'Travel Fees'),
        ('G', 'General'),
        ('V', 'Vendor Price Difference'),
        ('M', 'Management Fees'),
    ]

    job_estimate = models.ForeignKey(JobEstimate, on_delete=models.CASCADE, related_name='job_estimate_additional_fees')
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    type = models.CharField(max_length=1, choices=FEE_TYPE_CHOICES)
    percentage = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Job Estimate Additional Fees'

    def __str__(self):
        return str(self.job_estimate.id) + ' - ' + str(self.amount)