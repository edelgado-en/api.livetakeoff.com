from django.db import models

from .job_schedule import JobSchedule
from .retainer_service import RetainerService

class JobScheduleRetainerService(models.Model):

    job_schedule = models.ForeignKey(JobSchedule, on_delete=models.CASCADE, related_name='job_schedule_retainer_services')
    retainer_service = models.ForeignKey(RetainerService, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Job Schedule Retainer Services'

    def __str__(self):
        return str(self.job_schedule.id) + ' - ' + self.retainer_service.name