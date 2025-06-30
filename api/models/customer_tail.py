from django.db import models
from .customer import Customer

class CustomerTail(models.Model):

    STATUS_CHOICES = [
        ('O', 'OK'),
        ('I', 'In Maintenance'),
        ('N', 'No Flight History'),
        ('S', 'Service Due'),
    ]

    tail_number = models.CharField(max_length=50, unique=True)
    aircraft_type_name = models.CharField(null=True, blank=True, max_length=255, help_text='Name of the aircraft type associated with this tail number')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O', help_text='Current status of the tail')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tails')
    is_active = models.BooleanField(default=True)

    flights_since_last_interior_level_1_service = models.IntegerField(default=0, help_text='Number of flights since the last interior level 1 service')
    flights_since_last_interior_level_2_service = models.IntegerField(default=0, help_text='Number of flights since the last interior level 2 service')
    flights_since_last_exterior_level_1_service = models.IntegerField(default=0, help_text='Number of flights since the last exterior level 1 service')
    flights_since_last_exterior_level_2_service = models.IntegerField(default=0, help_text='Number of flights since the last exterior level 2 service')
    
    last_interior_level_1_service_date = models.DateTimeField(null=True, blank=True, help_text='Date of the last interior level 1 service')
    last_interior_level_2_service_date = models.DateTimeField(null=True, blank=True, help_text='Date of the last interior level 2 service')
    last_exterior_level_1_service_date = models.DateTimeField(null=True, blank=True, help_text='Date of the last exterior level 1 service')
    last_exterior_level_2_service_date = models.DateTimeField(null=True, blank=True, help_text='Date of the last exterior level 2 service')

    is_interior_level_1_service_due = models.BooleanField(default=False, help_text='Indicates if the interior level 1 service is due')
    is_interior_level_2_service_due = models.BooleanField(default=False, help_text='Indicates if the interior level 2 service is due')
    is_exterior_level_1_service_due = models.BooleanField(default=False, help_text='Indicates if the exterior level 1 service is due')
    is_exterior_level_2_service_due = models.BooleanField(default=False, help_text='Indicates if the exterior level 2 service is due')

    last_interior_level_1_location = models.CharField(max_length=4, null=True, blank=True, help_text='Airport initials for last known location for interior level 1 service')
    last_interior_level_2_location = models.CharField(max_length=4, null=True, blank=True, help_text='Airport initials for last known location for interior level 2 service')
    last_exterior_level_1_location = models.CharField(max_length=4, null=True, blank=True, help_text='Airport initials for last known location for exterior level 1 service')
    last_exterior_level_2_location = models.CharField(max_length=4, null=True, blank=True, help_text='Airport initials for last known location for exterior level 2 service')