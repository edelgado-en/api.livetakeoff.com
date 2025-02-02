from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from .job_service_assignment import GenericServiceAssignmentSerializer
from ..models import Job
from .basic_user import BasicUserSerializer
from .job_tag import JobTagSerializer
from .job_file import JobFileSerializer
from .job_follower_email import JobFollowerEmailSerializer

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
    follower_emails = JobFollowerEmailSerializer(many=True)
    discounted_price = serializers.DecimalField(max_digits=9, decimal_places=2, read_only=True, required=False)

    files = serializers.SerializerMethodField()

    def get_files(self, obj):
        # if the current user is_admin or is_staff, or belong to the group Account Managers then return all the files for this job
        user = self.context['request'].user
        
        if user.is_staff or user.is_superuser or user.groups.filter(name='Account Managers').exists():
            return JobFileSerializer(obj.files.all(), many=True, read_only=True).data
        elif user.profile.customer and user.profile.customer == obj.customer:   
            # if the current user is a customer user then only return the files that are public
            return JobFileSerializer(obj.files.filter(is_public=True), many=True, read_only=True).data
        else:
            # return empty array
            return []

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
            'tags',
            'files',
            'hours_worked',
            'minutes_worked',
            'number_of_workers',
            'labor_time',
            'is_publicly_confirmed',
            'confirmed_full_name',
            'confirmed_email',
            'confirmed_phone_number',
            'arrival_formatted_date',
            'departure_formatted_date',
            'complete_before_formatted_date',
            'discounted_price',
            'follower_emails',
            'enable_flightaware_tracking'
        )


