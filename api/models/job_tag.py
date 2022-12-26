from django.db import models
from .tag import Tag
from .job import Job


class JobTag(models.Model):
    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT, related_name='job_tags')

    def __str__(self):
        return str(self.job.id) + ' - ' + self.tag.name
