from django.db import models
from .vendor import Vendor

from cloudinary.models import CloudinaryField

class VendorFile(models.Model):

    FILE_TYPE_CHOICES = [
        ('I', 'Insurance'),
        ('W', 'W-9'),
        ('O', 'Other'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255, null=True)
    file = CloudinaryField('file', resource_type='auto', folder='vendor_files')
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='vendor_files', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    size = models.PositiveIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=1, choices=FILE_TYPE_CHOICES, blank=True, null=True)
    expiration_date = models.DateTimeField(blank=True, null=True, help_text='Applicable for insurance files')
    is_expired = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name_plural = 'Vendor Files'