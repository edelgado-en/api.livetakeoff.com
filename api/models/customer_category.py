from django.db import models
from .customer import Customer

class CustomerCategory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('customer', 'name')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = 'Customer Categories'