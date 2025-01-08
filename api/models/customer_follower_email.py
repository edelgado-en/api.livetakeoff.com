from django.db import models
from .customer import Customer

class CustomerFollowerEmail(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='follower_emails')
    email = models.EmailField(max_length=255)