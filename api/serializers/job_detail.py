from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from .job_service_assignment import JobServiceAssignmentSerializer
from ..models import Job

class JobDetailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    customer = CustomerSerializer()
    completeBy = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    estimatedETA = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    estimatedETD = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    requestDate = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    service_assignments = JobServiceAssignmentSerializer(many=True, read_only=True)
    retainer_service_assignments = JobServiceAssignmentSerializer(many=True, read_only=True)

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
            'aircraftType',
            'airport',
            'fbo',
            'customer',
            'special_instructions',
            'service_assignments',
            'retainer_service_assignments'
        )


