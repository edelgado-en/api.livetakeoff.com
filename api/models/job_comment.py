from django.db import models
from .job import Job

class JobComments(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.comment
        
    class Meta:
        verbose_name_plural = 'Job Comments'