from django.db import models
from django.utils.html import mark_safe
from .job import Job

class JobPhotos(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='photos')
    name = models.CharField(max_length=255, null=True)
    image = models.ImageField(upload_to='images/', blank=True)
    interior = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='job_photos', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self) -> str:
        return self.name

    @property
    def image_preview(self):
        if self.image:
            return mark_safe('<img src="{}" width="300" height="300" />'.format(self.image.url))
        return ""
    
    class Meta:
        verbose_name_plural = 'Job Photos'