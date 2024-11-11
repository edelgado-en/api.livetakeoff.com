from django.db import models
from .customer import Customer
from .price_list import PriceList
from .vendor import Vendor

class VendorCustomerPriceList(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_customer_price_lists')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='vendor_customer_price_lists')
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name='vendor_customer_price_lists')