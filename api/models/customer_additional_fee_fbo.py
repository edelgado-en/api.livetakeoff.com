from tabnanny import verbose
from django.db import models
from .customer_additional_fee import CustomerAdditionalFee
from .fbo import FBO

class CustomerAdditionalFeeFBO(models.Model):
    customer_additional_fee = models.ForeignKey(CustomerAdditionalFee, on_delete=models.CASCADE, related_name='fbos')
    fbo = models.ForeignKey(FBO, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Customer Additional Fee FBOs'
