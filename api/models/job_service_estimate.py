from django.db import models
from .job_estimate import JobEstimate
from .service import Service


class JobServiceEstimate(models.Model):
    job_estimate = models.ForeignKey(JobEstimate, on_delete=models.CASCADE, related_name='job_service_estimates')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Job Service Estimates'

    def __str__(self):
        return str(self.job_estimate.id) + ' - ' + self.service.name