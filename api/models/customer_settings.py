from django.db import models
from .customer import Customer

class CustomerSettings(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    show_spending_info = models.BooleanField(default=False)
    allow_cancel_job = models.BooleanField(default=False)
    #TODO: add FK to price list
    retainer_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    #TODO: add retainer_contract as PDF. Configure Cloudinary to allow PDF upload
    show_job_price = models.BooleanField(default=False)
    special_instructions = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.customer.name

    class Meta:
        verbose_name_plural = 'Customer Settings'