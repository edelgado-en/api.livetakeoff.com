from django.db import models
from .job import Job

class JobCommentCheck(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='comment_checks')
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    last_time_check = models.DateTimeField()