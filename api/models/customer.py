from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    billingAddress = models.TextField(blank=True, null=True)
    emailAddress = models.EmailField(blank=True, null=True)
    logo = models.ImageField(upload_to='customers/', blank=True)
    banner = models.ImageField(upload_to='customers/', blank=True)
    about = models.TextField(blank=True, null=True)
    # Point of contact
    contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts', null=True, blank=True)
    billingInfo = models.TextField(blank=True, null=True)

    phone_number = PhoneNumberField(blank=True, null=True)

    active = models.BooleanField(default=True)

    exterior_service_checker = models.PositiveIntegerField(
        default=0,
        verbose_name='Exterior Service Checker',
        help_text='Refers to the number of arrived flights to be checked before suggesting an exterior service level 2'
    )

    def __str__(self) -> str:
        return self.name