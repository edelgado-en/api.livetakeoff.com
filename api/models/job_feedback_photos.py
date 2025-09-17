from django.db import models
from .job_feedback import JobFeedback

class JobFeedbackPhotos(models.Model):
    """
    Photos associated with job feedback entries. The job feedback already has an optional image field,
    but this model allows for multiple photos to be linked to a single feedback entry.
    """
    job_feedback = models.ForeignKey(JobFeedback, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='images/', null=True, blank=True)