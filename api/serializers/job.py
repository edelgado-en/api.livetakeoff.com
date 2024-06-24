from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from ..models import (Job, JobCommentCheck, JobComments)

from .job_tag import JobTagSerializer

class JobSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    completeBy = serializers.DateTimeField(format="%m/%d %H:%M")
    completeByFullDate = serializers.DateTimeField(source="completeBy", format="%m/%d/%Y %H:%M")
    estimatedETA = serializers.DateTimeField(format="%m/%d %H:%M")
    estimatedETD = serializers.DateTimeField(format="%m/%d %H:%M")
    completion_date = serializers.DateTimeField(format="%m/%d %H:%M")
    tags = JobTagSerializer(many=True)
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
            'status',
            'purchase_order',
            'aircraftType',
            'airport',
            'fbo',
            'completeBy',
            'completeByFullDate',
            'estimatedETA',
            'estimatedETD',
            'completion_date',
            'on_site',
            'tags',
            'comments_count',
            'arrival_formatted_date',
            'departure_formatted_date',
            'complete_before_formatted_date'
            )

