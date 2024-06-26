from django.db import models
from .customer import Customer
from .price_list import PriceList

class CustomerSettings(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='customer_settings')
    show_spending_info = models.BooleanField(default=False)
    allow_cancel_job = models.BooleanField(default=False)
    retainer_amount = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    #TODO: add retainer_contract as PDF. Configure Cloudinary to allow PDF upload
    show_job_price = models.BooleanField(default=False)
    special_instructions = models.TextField(blank=True, null=True)
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name='customer_settings', null=True)

    enable_approval_process = models.BooleanField(default=False)

    enable_auto_assignment = models.BooleanField(default=False)

    enable_request_priority = models.BooleanField(default=False, help_text='If enabled, the customer will be able to request priority service when creating a job')

    def __str__(self) -> str:
        return self.customer.name

    class Meta:
        verbose_name_plural = 'Customer Settings'