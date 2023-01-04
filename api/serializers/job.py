from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from ..models import Job

from .job_tag import JobTagSerializer

class JobSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    completeBy = serializers.DateTimeField(format="%m/%d %H:%M")
    estimatedETA = serializers.DateTimeField(format="%m/%d %H:%M")
    estimatedETD = serializers.DateTimeField(format="%m/%d %H:%M")
    completion_date = serializers.DateTimeField(format="%m/%d %H:%M")
    tags = JobTagSerializer(many=True)

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
            'estimatedETD',
            'completion_date',
            'on_site',
            'tags'
            )

