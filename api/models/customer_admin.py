from django.db import models
from .customer_settings import CustomerSettings


class CustomerAdmin(models.Model):
    customer_setting = models.ForeignKey(CustomerSettings, on_delete=models.CASCADE, related_name='admins')
    admin = models.ForeignKey('auth.User', on_delete=models.PROTECT)
