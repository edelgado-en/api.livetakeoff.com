from rest_framework import serializers
from ..models import ExportJob

from .basic_user import BasicUserSerializer
from .customer import CustomerSerializer

class ExportJobSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user = BasicUserSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)

    created_at = serializers.DateTimeField(format="%B %d, %Y", read_only=True)

    class Meta:
        model = ExportJob
        fields = (
            'id',
            'user',
            'customer',
            'filename',
            'progress',
            'status',
            'params',
            'created_at',
        )