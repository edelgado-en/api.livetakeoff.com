from rest_framework import serializers
from .basic_user import BasicUserSerializer
from api.models import JobStatusActivity


class CustomerActivitySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user = BasicUserSerializer()
    tailNumber = serializers.ReadOnlyField()

    class Meta:
        model = JobStatusActivity
        fields = (
            'id',
            'status',
            'user',
            'timestamp',
            'tailNumber'
            )