from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from ..models import Job

class JobSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    completeBy = serializers.DateTimeField(format="%b-%d %I:%M %p")
    estimatedETA = serializers.DateTimeField(format="%b-%d %I:%M %p")
    completion_date = serializers.DateTimeField(format="%b-%d %I:%M %p")

    class Meta:
        model = Job
        fields = (
            'id',
            'tailNumber',
            'status',
            'purchase_order',
            'aircraftType',
            'airport',
            'fbo',
            'completeBy',
            'estimatedETA',
            'completion_date',
            'on_site'
            )

