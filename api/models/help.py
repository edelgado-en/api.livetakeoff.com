from django.db import models

from cloudinary.models import CloudinaryField

class Help(models.Model):
    ACCESS_LEVEL_CHOICES = [
        ('A', 'All'),
        ('C', 'Customer'),
        ('E', 'External Project Manager'),
        ('P', 'Internal Project Manager'),
        ('I', 'Internal Coordinator'),
        ('D', 'Admin'),
    ]

    TYPE_CHOICES = [
        ('F', 'File'),
        ('P', 'Photo'),
        ('U', 'URL'),
    ]

    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True, blank=True)
    file = CloudinaryField('file', resource_type='auto', folder='help_files', blank=True)
    photo = models.ImageField(upload_to='help/', blank=True)
    url = models.URLField(max_length=200, blank=True)
    file_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='F')
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='help_files', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    access_level = models.CharField(max_length=1, choices=ACCESS_LEVEL_CHOICES, default='A')