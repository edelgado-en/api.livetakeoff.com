from django.db import models
from .customer import Customer
from .aircraft_type import AircraftType
from .airport import Airport
from .fbo import FBO
from .service import Service
from .retainer_service import RetainerService

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

    ]
    #TODO: figure out how to do the purchase order number. Do it as a separate column
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='jobs')
    requestDate = models.DateTimeField(auto_now_add=True)
    tailNumber = models.CharField(max_length=50)
    aircraftType = models.ForeignKey(AircraftType, on_delete=models.PROTECT)
    airport = models.ForeignKey(Airport, on_delete=models.PROTECT)
    fbo = models.ForeignKey(FBO, on_delete=models.PROTECT)
    estimatedETA = models.DateTimeField(blank=True, null=True)
    estimatedETD = models.DateTimeField(blank=True, null=True)
    completeBy = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    services = models.ManyToManyField(Service, related_name='services', blank=True)
    retainerServices = models.ManyToManyField(RetainerService, related_name='retainerservices', blank=True)
    assignees = models.ManyToManyField('auth.User', related_name='assignees', blank=True)

    def __str__(self) -> str:
        return str(self.id) + ' - ' + self.tailNumber + ' - ' + self.airport.initials + ' - ' + self.aircraftType.name