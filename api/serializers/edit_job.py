from django.db import models
from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from ..models import Job

class JobService(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)


class JobEditSerializer(serializers.ModelSerializer):
    estimatedETA = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p", required=False, allow_null=True)
    estimatedETD = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p", required=False, allow_null=True)
    completeBy = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p", required=False, allow_null=True)


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