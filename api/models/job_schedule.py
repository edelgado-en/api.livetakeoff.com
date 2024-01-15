from django.db import models

from .customer import Customer
from .aircraft_type import AircraftType
from .airport import Airport
from .fbo import FBO

class JobSchedule(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='schedules')
    tailNumber = models.CharField(max_length=50)
    aircraftType = models.ForeignKey(AircraftType, on_delete=models.PROTECT)
    airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='schedules')
    fbo = models.ForeignKey(FBO, on_delete=models.PROTECT)

    is_deleted = models.BooleanField(default=False)

    is_recurrent = models.BooleanField(default=False)

    start_date = models.DateTimeField(blank=True, null=True, help_text='Used for non-recurrent schedules')    
    repeat_every = models.PositiveIntegerField(blank=True, null=True, help_text='Used for recurrent schedules. It refers to days.')

    last_job_created_at = models.DateTimeField(blank=True, null=True)

    comment = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey('auth.User', related_name='schedules', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self) -> str:
        return str(self.id) + ' - ' + self.tailNumber + ' - ' + self.airport.initials + ' - ' + self.aircraftType.name