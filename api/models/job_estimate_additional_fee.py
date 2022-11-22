from django.db import models
from .job_estimate import JobEstimate


class JobEstimateAdditionalFee(models.Model):
    FEE_TYPE_CHOICES = [
        ('F', 'By FBO'),
        ('A', 'By Airport'),
        ('G', 'General'),
    ]

    job_estimate = models.ForeignKey(JobEstimate, on_delete=models.CASCADE, related_name='job_estimate_additional_fees')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    type = models.CharField(max_length=1, choices=FEE_TYPE_CHOICES)
    percentage = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Job Estimate Additional Fees'

    def __str__(self):
        return str(self.job_estimate.id) + ' - ' + str(self.amount)