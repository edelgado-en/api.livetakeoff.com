from django.db import models
from api.models import (TailAlert)

from cloudinary.models import CloudinaryField

class TailFile(models.Model):
    tail_alert = models.ForeignKey(TailAlert, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255, null=True)
    file = CloudinaryField('file', resource_type='auto', folder='tail_files')
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='tail_files', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    size = models.PositiveIntegerField(blank=True, null=True)
    is_public = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name_plural = 'Tail Files'