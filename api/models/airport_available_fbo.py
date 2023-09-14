from django.db import models
from .airport import Airport
from .fbo import FBO

class AirportAvailableFbo(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='available_fbos')
    fbo = models.ForeignKey(FBO, on_delete=models.PROTECT, related_name='available_airports')