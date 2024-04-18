from rest_framework import serializers
from ..models import Job

class JobService(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)


class JobEditSerializer(serializers.ModelSerializer):
    estimatedETA = serializers.DateTimeField(format="%m/%d/%y %H:%M", required=False, allow_null=True)
    estimatedETD = serializers.DateTimeField(format="%m/%d/%y %H:%M", required=False, allow_null=True)
    completeBy = serializers.DateTimeField(format="%m/%d/%y %H:%M", required=False, allow_null=True)


    class Meta:
        model = Job
        fields = (
            'tailNumber',
            'customer_purchase_order',
            'customer',
            'status',
            'aircraftType',
            'airport',
            'fbo',
            'estimatedETA',
            'estimatedETD',
            'completeBy',
            'price',
            'on_site',
            'requested_by',
            'hours_worked',
            'minutes_worked',
            'number_of_workers',
            'labor_time'
            )