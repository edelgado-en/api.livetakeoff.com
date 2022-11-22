from django.db import models
from .job_estimate import JobEstimate


class JobEstimateDiscount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('S', 'By Service'),
        ('A', 'By Airport'),
        ('G', 'General'),
    ]

    job_estimate = models.ForeignKey(JobEstimate, on_delete=models.CASCADE, related_name='job_estimate_discounts')
    amount = models.IntegerField()
    type = models.CharField(max_length=1, choices=DISCOUNT_TYPE_CHOICES)
    percentage = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Job Estimate Discounts'

    def __str__(self):
        return str(self.job_estimate.id) + ' - ' + str(self.amount)


