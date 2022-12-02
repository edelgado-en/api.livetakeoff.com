from django.db import models
from .job import Job
from .service import Service


class ServiceActivity(models.Model):
    STATUS_CHOICES = [
        ('W', 'WIP'),
        ('C', 'Complete'),
    ]

    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='activities')
    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name='service_activities')
    project_manager = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='service_activities')