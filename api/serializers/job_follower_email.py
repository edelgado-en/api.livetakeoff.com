from rest_framework import serializers
from ..models import (
    JobFollowerEmail
    )

class JobFollowerEmailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()

    class Meta:
        model = JobFollowerEmail
        fields = ['id', 'email']