from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from ..models import Job

class JobDetailBasicSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()

    class Meta:
        model = Job
        fields = (
            'id',
            'tailNumber',
            'status',
            'purchase_order',
            'aircraftType',
            'airport',
        )
