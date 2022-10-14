from django.db import models
from .job import Job
from .service import Service

class JobServiceAssignment(models.Model):
    STATUS_CHOICES = [
        ('U', 'Unassigned'),
        ('A', 'Assigned'),
        ('W', 'WIP'),
        ('C', 'Completed'),
    ]

    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name='job_service_assignments')
    project_manager = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='job_service_assignments', null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='U')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_job_service_assignment'
        verbose_name_plural = 'Job Service Assignments'

    def __str__(self):
        return str(self.job.id) + ' - ' + self.service.name + ' - ' + self.status
