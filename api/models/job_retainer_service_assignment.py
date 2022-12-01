from django.db import models
from .job import Job
from .retainer_service import RetainerService

class JobRetainerServiceAssignment(models.Model):
    STATUS_CHOICES = [
        ('U', 'Unassigned'),
        ('A', 'Assigned'),
        ('W', 'WIP'),
        ('C', 'Completed'),
    ]

    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name='job_retainer_service_assignments')
    project_manager = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='job_retainer_service_assignments', null=True, blank=True)
    retainer_service = models.ForeignKey(RetainerService, on_delete=models.PROTECT)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='U')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Job Retainer Service Assignments'

    def __str__(self):
        return str(self.job.id) + ' - ' + self.retainer_service.name
