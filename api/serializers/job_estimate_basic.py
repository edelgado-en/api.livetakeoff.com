from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .basic_user import BasicUserSerializer
from .customer import CustomerSerializer
from .job_basic import JobBasicSerializer
from .fbo import FBOSerializer
from .airport import AirportSerializer

from api.models import JobEstimate


class JobEstimateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    aircraftType = AircraftTypeSerializer()
    customer = CustomerSerializer()
    job = JobBasicSerializer(read_only=True)
    airport = AirportSerializer()
    fbo = FBOSerializer()
    requested_by = BasicUserSerializer()

    class Meta:
        model = JobEstimate
        fields = (
            'id',
            'requested_at',
            'requested_by',
            'processed_at',
            'aircraftType',
            'customer',
            'status',
            'is_processed',
            'tailNumber',
            'services_price',
            'discounted_price',
            'total_price',
            'job',
            'airport',
            'fbo',
        )