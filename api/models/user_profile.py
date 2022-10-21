from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from .vendor import Vendor
from .customer import Customer

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='user_profiles', null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='user_profiles', null=True, blank=True)
    email_notifications = models.BooleanField(default=True)
    allow_set_as_busy = models.BooleanField(default=False)
    about = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)

