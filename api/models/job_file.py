from django.db import models
from .job import Job

from cloudinary.models import CloudinaryField

class JobFiles(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255, null=True)
    file = CloudinaryField('file', resource_type='auto', folder='job_files')
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='job_files', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    size = models.PositiveIntegerField(blank=True, null=True)
    customer_uploaded = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name_plural = 'Job Files'