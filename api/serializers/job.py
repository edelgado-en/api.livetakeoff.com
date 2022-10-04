from rest_framework import serializers
from ..models import Job

class JobSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Job
        fields = ('id', 'tailNumber', 'status')