from django.db import models
from .job import Job

class JobStatusActivity(models.Model):
    STATUS_CHOICES = [
        ('A', 'Accepted'),
        ('S', 'Assigned'),
        ('U', 'Submitted'),
        ('W', 'WIP'),
        ('C', 'Complete'),
        ('T', 'Cancelled'),
        ('R', 'Review'),
        ('I', 'Invoiced'),
        ('P', 'Price Changed'),
        ('X', 'Project Manager Unassigned')
    ]

    ACTIVITY_TYPE_CHOICES = [
        ('E', 'Departure Changed'),
        ('A', 'Arrival Changed'), 
        ('B', 'Complete Before Changed'),
        ('P', 'Price Changed'),
        ('O', 'Airport Changed'),
        ('F', 'FBO Changed'),
        ('S', 'Status Changed'),
        ('T', 'Tail Number Changed'),
        ('U', 'Photos Uploaded'),
        ('R', 'Job Returned'),
    ]

    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPE_CHOICES, default='S')

    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name='status_activities')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='status_activities')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Job Status Activities'