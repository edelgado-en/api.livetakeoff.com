from django.db import models
from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from ..models import Job

class JobEditSerializer(serializers.ModelSerializer):
    estimatedETA = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    estimatedETD = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    completeBy = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")


    class Meta:
        model = Job
        fields = (
            'tailNumber',
            'customer',
            'status',
            'aircraftType',
            'airport',
            'fbo',
            'estimatedETA',
            'estimatedETD',
            'completeBy'
            )