from django.db import models
from .aircraft_type import AircraftType
from .service import Service

class EstimatedServiceTime(models.Model):
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='estimated_service_times')
    estimated_time = models.PositiveIntegerField(verbose_name='Estimated Time (minutes)')

    class Meta:
        verbose_name_plural = 'Estimated Service Times'