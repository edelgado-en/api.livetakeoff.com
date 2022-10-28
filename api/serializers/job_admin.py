from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from ..models import Job
from .job_service_assignment import (
        JobServiceAssignmentSerializer,
        JobRetainerServiceAssignmentSerializer
    )

class JobAdminSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    customer = CustomerSerializer()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    completeBy = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    estimatedETA = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    estimatedETD = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    requestDate = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p", read_only=True)
    job_service_assignments = JobServiceAssignmentSerializer(many=True)
    job_retainer_service_assignments = JobRetainerServiceAssignmentSerializer(many=True)

    class Meta:
        model = Job
        fields = (
            'id',
            'tailNumber',
            'requestDate',
            'estimatedETA',
            'estimatedETD',
            'completeBy',
            'status',
            'customer',
            'purchase_order',
            'aircraftType',
            'airport',
            'fbo',
            'completeBy',
            'job_service_assignments',
            'job_retainer_service_assignments',
            'price',
            'is_auto_priced'
            )
