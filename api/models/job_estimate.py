from django.db import models
from .customer import Customer
from .aircraft_type import AircraftType
from .airport import Airport
from .job import Job
from .fbo import FBO


class JobEstimate(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('R', 'Rejected'),
    ]

    requested_at = models.DateTimeField(auto_now_add=True, blank=True)
    requested_by = models.ForeignKey('auth.User', related_name='job_estimates', on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='job_estimates')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(blank=True, null=True)

    #to be updated once a job is created based on this estimate
    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name='job_estimates', blank=True, null=True)
    tailNumber = models.CharField(max_length=50, blank=True, null=True)
    aircraftType = models.ForeignKey(AircraftType, on_delete=models.PROTECT)
    airport = models.ForeignKey(Airport, on_delete=models.PROTECT, blank=True, null=True)
    fbo = models.ForeignKey(FBO, on_delete=models.PROTECT, blank=True, null=True)

    # the summation of the price of all the services in the estimate. This is here for quick lookups
    services_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)

    # This is the price of the services after applying discounts, if any. This is here for quick lookups
    discounted_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)

    # This is the total price of the estimated after applying discounts and applying additional fees. This is here for quick lookups
    total_price = models.DecimalField(max_digits=9, decimal_places=2, null=True)

    def __str__(self) -> str:
        return str(self.id) + ' - ' + self.tailNumber + ' - ' + self.aircraftType.name