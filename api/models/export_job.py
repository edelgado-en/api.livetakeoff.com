from django.db import models
from django.conf import settings

from .customer import Customer

class ExportJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        RUNNING = "RUNNING"
        SUCCEEDED = "SUCCEEDED"
        FAILED = "FAILED"
        CANCELED = "CANCELED"

    JOB_TYPE = [
        ('J', 'Jobs'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='export_jobs')
    params = models.JSONField(default=dict, blank=True)         # filters from UI
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    job_type = models.CharField(max_length=1, choices=JOB_TYPE, default='J')
    progress = models.IntegerField(default=0)                   # 0..100
    file_bytes = models.BinaryField(null=True, blank=True)      # zipped CSV
    filename = models.CharField(max_length=200, blank=True)     # e.g. jobs_2025-08-15.zip
    error_message = models.TextField(blank=True)
    task_id = models.CharField(max_length=50, null=True, blank=True)
    cancel_requested = models.BooleanField(default=False)       # for cooperative cancel
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ExportJob #{self.pk} ({self.status})"