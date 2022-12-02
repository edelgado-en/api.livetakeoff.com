from django.db import models
from .job import Job
from .retainer_service import RetainerService


class RetainerServiceActivity(models.Model):
    STATUS_CHOICES = [
        ('W', 'WIP'),
        ('C', 'Complete'),
    ]

    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    retainer_service = models.ForeignKey(RetainerService, on_delete=models.PROTECT, related_name='activities')
    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name='retainer_service_activities')
    project_manager = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='retainer_service_activities')