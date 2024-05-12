from django.db import models
from .customer import Customer
from .aircraft_type import AircraftType
from .airport import Airport
from .fbo import FBO
from .service import Service
from .retainer_service import RetainerService
from .job_schedule import JobSchedule
from .vendor import Vendor

class Job(models.Model):
    STATUS_CHOICES = [
        ('A', 'Accepted'),
        ('S', 'Assigned'),
        ('U', 'Submitted'),
        ('W', 'WIP'),
        ('C', 'Complete'),
        ('T', 'Cancelled'),
        ('R', 'Review'),
        ('I', 'Invoiced'),
        ('N', 'Not Invoiced'),
    ]

       # This is duplicated. I already have requestDate
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    purchase_order = models.CharField(max_length=255, blank=True, null=True)

    # provided by the customer
    customer_purchase_order = models.CharField(max_length=255, blank=True, null=True)

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='jobs')
    requestDate = models.DateTimeField(auto_now_add=True)
    tailNumber = models.CharField(max_length=50)
    aircraftType = models.ForeignKey(AircraftType, on_delete=models.PROTECT)
    airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='jobs')
    fbo = models.ForeignKey(FBO, on_delete=models.PROTECT)
    estimatedETA = models.DateTimeField(blank=True, null=True)
    estimatedETD = models.DateTimeField(blank=True, null=True)
    completeBy = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    created_by = models.ForeignKey('auth.User', related_name='jobs', on_delete=models.CASCADE, blank=True, null=True)

    # Sometimes user needs to add the name of the person requesting the job. This is a free form field. Optional.
    requested_by = models.CharField(max_length=255, blank=True, null=True)

    completion_date = models.DateTimeField(blank=True, null=True)

    # Saved in minutes. Add all the estimated times for the services in the job based on aircraft type
    estimated_completion_time = models.PositiveIntegerField(blank=True, null=True, verbose_name='Estimated Completion Time (minutes)')
    
    # saved in minutes. Calculated when setting a job as complete with the actual time it took from WIP to completed status
    # by reading the job status activity table
    actual_completion_time = models.PositiveIntegerField(blank=True, null=True, verbose_name='Actual Completion Time (minutes)') 

    price = models.DecimalField(max_digits=9, decimal_places=2, null=True)

    is_auto_priced = models.BooleanField(default=True)

    on_site = models.BooleanField(default=False)

    number_of_workers = models.PositiveIntegerField(blank=True, null=True)

    hours_worked = models.PositiveIntegerField(blank=True, null=True)

    minutes_worked = models.PositiveIntegerField(blank=True, null=True)

    labor_time = models.FloatField(blank=True, null=True)

    job_schedule = models.ForeignKey(JobSchedule, on_delete=models.PROTECT, blank=True, null=True)

    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, blank=True, null=True, related_name='jobs')

    vendor_charge = models.DecimalField(max_digits=9, decimal_places=2, null=True)

    vendor_additional_cost = models.DecimalField(max_digits=9, decimal_places=2, null=True)

    internal_additional_cost = models.DecimalField(max_digits=9, decimal_places=2, null=True)

    subcontractor_profit = models.DecimalField(max_digits=9, decimal_places=2, null=True, help_text='Calculated by subtracting the vendor charge and additional cost from the price')

    is_publicly_confirmed = models.BooleanField(default=False, help_text='It is set to true when the job is confirmed via a public link.')

    confirmed_full_name = models.CharField(max_length=300, blank=True, null=True)

    confirmed_email = models.CharField(max_length=320, blank=True, null=True)

    confirmed_phone_number = models.CharField(max_length=255, blank=True, null=True)

    accepted_full_name = models.CharField(max_length=300, blank=True, null=True, help_text='This is the name of the vendor that accepted the job via the shareable public link')

    accepted_email = models.CharField(max_length=320, blank=True, null=True)

    accepted_phone_number = models.CharField(max_length=255, blank=True, null=True)

    returned_full_name = models.CharField(max_length=300, blank=True, null=True, help_text='This is the name of the vendor that returned the job via the shareable public link')

    returned_email = models.CharField(max_length=320, blank=True, null=True)

    returned_phone_number = models.CharField(max_length=255, blank=True, null=True)

    travel_fees_amount_applied = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    fbo_fees_amount_applied = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    vendor_higher_price_amount_applied = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    management_fees_amount_applied = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    arrival_formatted_date = models.CharField(max_length=255, blank=True, null=True, help_text='This is the formatted date for the arrival date and time of the job to avoid complications with timezones when sending emails and sms notifica')

    departure_formatted_date = models.CharField(max_length=255, blank=True, null=True)

    complete_before_formatted_date = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.id) + ' - ' + self.tailNumber + ' - ' + self.airport.initials + ' - ' + self.aircraftType.name