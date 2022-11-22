from rest_framework import serializers
from ..models import Job

class JobBasicSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta:
        model = Job
        fields = (
            'id',
            'tailNumber',
            'status',
            )