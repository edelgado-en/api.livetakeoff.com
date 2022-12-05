from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from .job_service_assignment import GenericServiceAssignmentSerializer
from ..models import Job
from .basic_user import BasicUserSerializer
from .job_photo import JobPhotoSerializer
from .job_comment import JobCommentSerializer


class SharedJobDetailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    customer = CustomerSerializer()
    completeBy = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    estimatedETA = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    estimatedETD = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p")
    requestDate = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p", read_only=True)
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    service_assignments = GenericServiceAssignmentSerializer(many=True, read_only=True)
    retainer_service_assignments = GenericServiceAssignmentSerializer(many=True, read_only=True)
    job_photos = JobPhotoSerializer(many=True, read_only=True)
    job_comments = JobCommentSerializer(many=True, read_only=True)
    created_by = BasicUserSerializer(read_only=True)

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
            'retainer_service_assignments',
            'job_photos',
            'job_comments',
            'on_site',
            'created_by',
            'requested_by'
        )