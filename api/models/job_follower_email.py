from django.db import models
from .job import Job

class JobFollowerEmail(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='follower_emails')
    email = models.EmailField(max_length=255)