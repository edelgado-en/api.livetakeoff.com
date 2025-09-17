from django.db import models
from .job import Job

class JobFeedback(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='feedbacks')
    comment = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    author = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)