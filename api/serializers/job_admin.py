from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from ..models import (Job, JobCommentCheck, JobComments)
from .job_service_assignment import (
        JobServiceAssignmentSerializer,
        JobRetainerServiceAssignmentSerializer,
    )

from .job_tag import JobTagSerializer

from .basic_user import BasicUserSerializer

class JobAdminSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    customer = CustomerSerializer()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    completeBy = serializers.DateTimeField(format="%m/%d %H:%M")
    completeByFullDate = serializers.DateTimeField(source="completeBy", format="%Y-%m-%d %H:%M")
    estimatedETA = serializers.DateTimeField(format="%m/%d %H:%M")
    estimatedETD = serializers.DateTimeField(format="%m/%d %H:%M")
    requestDate = serializers.DateTimeField(format="%m/%d %H:%M", read_only=True)
    job_service_assignments = JobServiceAssignmentSerializer(many=True)
    job_retainer_service_assignments = JobRetainerServiceAssignmentSerializer(many=True)
    tags = JobTagSerializer(many=True)
    created_by = BasicUserSerializer(read_only=True)
    completion_date = serializers.DateTimeField(format="%m/%d %H:%M", read_only=True)
    comments_count = serializers.SerializerMethodField()

    def get_comments_count(self, obj):
        comments_count = 0

        request = self.context.get('request')
        
        if request:
            try:
                job_comment_check = JobCommentCheck.objects.get(job=obj, user=request.user)
                qs = JobComments.objects.filter(job=obj, created__gt=job_comment_check.last_time_check).exclude(author=self.context['request'].user)
                if request.user.profile.customer and request.user.profile.customer == obj.customer:
                    qs = qs.filter(is_public=True)
                comments_count = qs.count()
            except JobCommentCheck.DoesNotExist:
                qs = JobComments.objects.filter(job=obj).exclude(author=request.user)
                if request.user.profile.customer and request.user.profile.customer == obj.customer:
                    qs = qs.filter(is_public=True)
                comments_count = qs.count()
        
        return comments_count

    class Meta:
        model = Job
        fields = (
            'id',
            'tailNumber',
            'requestDate',
            'estimatedETA',
            'estimatedETD',
            'completeBy',
            'completeByFullDate',
            'status',
            'customer',
            'purchase_order',
            'customer_purchase_order',
            'aircraftType',
            'airport',
            'fbo',
            'completeBy',
            'job_service_assignments',
            'job_retainer_service_assignments',
            'tags',
            'price',
            'is_auto_priced',
            'on_site',
            'created_by',
            'completion_date',
            'internal_additional_cost',
            'vendor_additional_cost',
            'vendor_charge',
            'comments_count'
            )
