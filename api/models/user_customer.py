from django.db import models
from django.contrib.auth.models import User
from .customer import Customer

class UserCustomer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_customers')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='user_customers')

    class Meta:
        unique_together = ['user', 'customer']

    def __str__(self) -> str:
        return f'{self.user} - {self.customer}'