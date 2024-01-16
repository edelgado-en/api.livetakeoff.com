from django.db import models
from .tag import Tag
from .job_schedule import JobSchedule

class JobScheduleTag(models.Model):
    job_schedule = models.ForeignKey(JobSchedule, on_delete=models.PROTECT, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT, related_name='job_schedule_tags')

    def __str__(self):
        return str(self.job_schedule.id) + ' - ' + self.tag.name