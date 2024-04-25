from django.db import models
from .job import Job

class JobAcceptanceNotification(models.Model):

    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name='acceptance_notifications')
    project_manager = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='acceptance_notifications')
    attempt = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)