from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from ..models import (Job, JobCommentCheck, JobComments)

class JobCompletedSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    customer = CustomerSerializer()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    completeBy = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    estimatedETA = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    estimatedETD = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    requestDate = serializers.DateTimeField(format="%m/%d/%y %H:%M", read_only=True)
    completion_date = serializers.DateTimeField(format="%m/%d/%y %H:%M", read_only=True)
    comments_count = serializers.IntegerField(read_only=True, default=0)

    """ THIS IS CAUSING MASSIVE PERFORMANCE ISSUES """
    """ def get_comments_count(self, obj):
        comments_count = 0

        request = self.context.get('request')
        
        if request:
            try:
                job_comment_check = JobCommentCheck.objects.get(job=obj, user=request.user)
                qs = JobComments.objects.filter(job=obj, created__gt=job_comment_check.last_time_check).exclude(author=self.context['request'].user)
                
                if request.user.profile.customer:
                    qs = qs.filter(is_public=True)
                
                comments_count = qs.count()
            
            except JobCommentCheck.DoesNotExist:
                qs = JobComments.objects.filter(job=obj).exclude(author=request.user)
                
                if request.user.profile.customer:
                    qs = qs.filter(is_public=True)
                
                comments_count = qs.count()
        
        return comments_count """

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
            'customer_purchase_order',
            'aircraftType',
            'airport',
            'fbo',
            'completeBy',
            'price',
            'is_auto_priced',
            'on_site',
            'completion_date',
            'labor_time',
            'travel_fees_amount_applied',
            'fbo_fees_amount_applied',
            'vendor_higher_price_amount_applied',
            'management_fees_amount_applied',
            'arrival_formatted_date',
            'departure_formatted_date',
            'complete_before_formatted_date',
            'comments_count'
            )
