from django.db import models
from .customer_settings import CustomerSettings

class CustomerAdditionalFee(models.Model):
    FEE_TYPE_CHOICES = [
        ('F', 'By FBO'),
        ('A', 'By Airport'),
        ('G', 'General'),
    ]

    customer_setting = models.ForeignKey(CustomerSettings, on_delete=models.CASCADE, related_name='fees')
    fee = models.DecimalField(max_digits=9, decimal_places=2)
    type = models.CharField(max_length=1, choices=FEE_TYPE_CHOICES)
    percentage = models.BooleanField(default=False)

    def __str__(self) -> str:
        return 'id: ' + str(self.id) + ' type: ' + str(self.type) + ' fee: $' + str(self.fee) 

    class Meta:
        verbose_name_plural = 'Customer Additional Fees'