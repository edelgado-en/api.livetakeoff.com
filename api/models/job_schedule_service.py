from django.db import models

from .job_schedule import JobSchedule
from .service import Service

class JobScheduleService(models.Model):

    job_schedule = models.ForeignKey(JobSchedule, on_delete=models.CASCADE, related_name='job_schedule_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Job Schedule Services'

    def __str__(self):
        return str(self.job_schedule.id) + ' - ' + self.service.name