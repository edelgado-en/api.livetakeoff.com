from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from .basic_user import BasicUserSerializer

from ..models import JobSchedule

class JobScheduleSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    customer = CustomerSerializer()
    start_date = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    last_job_created_at = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    created_by = BasicUserSerializer(read_only=True)

    class Meta:
        model = JobSchedule
        fields = (
            'id',
            'tailNumber',
            'aircraftType',
            'airport',
            'fbo',
            'customer',
            'is_recurrent',
            'repeat_every',
            'start_date',
            'created_by',
            )