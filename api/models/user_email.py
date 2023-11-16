from django.contrib.auth.models import User
from django.db import models

class UserEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_emails')
    email = models.EmailField(max_length=255)

    class Meta:
        unique_together = ['user', 'email']

    def __str__(self) -> str:
        return self.email