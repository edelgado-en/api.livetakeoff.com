from rest_framework import serializers
from .basic_user import BasicUserSerializer
from api.models import JobStatusActivity


class JobActivitySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user = BasicUserSerializer()

    class Meta:
        model = JobStatusActivity
        fields = (
            'id',
            'status',
            'price',
            'user',
            'timestamp',
            )