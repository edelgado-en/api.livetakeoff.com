from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from .job_service_assignment import GenericServiceAssignmentSerializer
from ..models import Job
from .basic_user import BasicUserSerializer
from .job_tag import JobTagSerializer

class JobDetailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    customer = CustomerSerializer()
    completeBy = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    estimatedETA = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    estimatedETD = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    requestDate = serializers.DateTimeField(format="%m/%d/%y %H:%M", read_only=True)
    completion_date = serializers.DateTimeField(format="%m/%d/%y %H:%M", read_only=True)
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    service_assignments = GenericServiceAssignmentSerializer(many=True, read_only=True)
    retainer_service_assignments = GenericServiceAssignmentSerializer(many=True, read_only=True)
    total_photos = serializers.IntegerField(read_only=True)
    total_assignees = serializers.IntegerField(read_only=True)
    created_by = BasicUserSerializer(read_only=True)
    encoded_id = serializers.CharField(max_length=100, read_only=True, required=False)
    tags = JobTagSerializer(many=True)

    class Meta:
        model = Job
        fields = (
            'id',
            'tailNumber',
            'completeBy',
            'estimatedETA',
            'estimatedETD',
            'requestDate',
            'status',
            'purchase_order',
            'customer_purchase_order',
            'aircraftType',
            'airport',
            'fbo',
            'customer',
            'special_instructions',
            'service_assignments',
            'retainer_service_assignments',
            'total_photos',
            'total_assignees',
            'price',
            'is_auto_priced',
            'on_site',
            'created_by',
            'requested_by',
            'completion_date',
            'encoded_id',
            'tags'
        )


