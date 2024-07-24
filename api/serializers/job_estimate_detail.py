from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .basic_user import BasicUserSerializer
from .customer import CustomerSerializer
from .job_basic import JobBasicSerializer
from .fbo import FBOSerializer
from .airport import AirportSerializer

from api.models import JobEstimate


class EstimateServiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField()
    category = serializers.CharField()


class JobEstimateDiscountSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    percentage = serializers.BooleanField()
    type = serializers.CharField()


class JobEstimateAdditionalFeeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)
    percentage = serializers.BooleanField()
    type = serializers.CharField()


class JobEstimateDetailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    aircraftType = AircraftTypeSerializer()
    customer = CustomerSerializer()
    job = JobBasicSerializer(read_only=True)
    airport = AirportSerializer()
    fbo = FBOSerializer()
    requested_by = BasicUserSerializer()
    services = EstimateServiceSerializer(many=True, read_only=True)
    job_estimate_discounts = JobEstimateDiscountSerializer(many=True, read_only=True)
    job_estimate_additional_fees = JobEstimateAdditionalFeeSerializer(many=True, read_only=True)
    encoded_id = serializers.CharField(max_length=100, read_only=True, required=False)

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
            'services',
            'job_estimate_discounts',
            'job_estimate_additional_fees',
            'encoded_id',
            'show_totals'     
        )