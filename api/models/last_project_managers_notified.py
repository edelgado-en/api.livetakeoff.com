from django.db import models
from .job import Job

class LastProjectManagersNotified(models.Model):

    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name='project_managers_notified')
    project_manager = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='project_managers_notified')